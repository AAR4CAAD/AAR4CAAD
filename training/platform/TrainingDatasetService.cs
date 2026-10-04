using AestheticArchitectureResearch.Application.Common;
using AestheticArchitectureResearch.Domain;
using AestheticArchitectureResearch.Infrastructure.Data;
using Microsoft.EntityFrameworkCore;

namespace AestheticArchitectureResearch.Application.Services;

public class ControlRequest
{
    public int ReferenceDatasetId { get; set; }
    public ControlSelectionMethod Method { get; set; } = ControlSelectionMethod.MatchedControl;
    public int? Seed { get; set; }
    /// <summary>Variables for stratification/matching: BuildingType, Period, Country, Continent, Style, IndustrialOrNonIndustrial, AspectRatio.</summary>
    public List<string> Variables { get; set; } = new() { "BuildingType", "Period" };
    /// <summary>
    /// If true, images of the reference (aesthetic) dataset are removed from the sampling pool (disjoint sets).
    /// If false, the control is sampled from the whole active corpus, i.e. strictly without any aesthetic criterion.
    /// </summary>
    public bool ExcludeReferenceImages { get; set; }
}

/// <summary>
/// Training datasets (AESTHETIC, CONTROL, …): generation, versioning and scientific freeze.
/// A frozen dataset can never be modified; changes require a new version (or an audited administrator override).
/// </summary>
public class TrainingDatasetService
{
    private readonly AppDbContext _db;
    private readonly SelectionService _selection;
    private readonly AuditService _audit;

    public TrainingDatasetService(AppDbContext db, SelectionService selection, AuditService audit)
    {
        _db = db;
        _selection = selection;
        _audit = audit;
    }

    public static readonly string[] MatchingVariables = { "BuildingType", "Period", "Country", "Continent", "Style", "IndustrialOrNonIndustrial", "AspectRatio" };

    public Task<List<TrainingDataset>> ListAsync(int experimentId, CancellationToken ct = default)
        => _db.TrainingDatasets.AsNoTracking().Include(d => d.Items).Include(d => d.SelectionRule)
            .Where(d => d.ExperimentId == experimentId).OrderBy(d => d.Type).ThenByDescending(d => d.Version).ToListAsync(ct);

    public async Task<TrainingDataset> GetAsync(int experimentId, int id, CancellationToken ct = default)
        => await _db.TrainingDatasets.Include(d => d.Items).ThenInclude(i => i.ImageAsset!).ThenInclude(a => a.Captions)
               .Include(d => d.SelectionRule)
               .FirstOrDefaultAsync(d => d.Id == id && d.ExperimentId == experimentId, ct) ?? throw new NotFoundException(nameof(TrainingDataset), id);

    private async Task<int> NextVersionAsync(int experimentId, TrainingDatasetType type, CancellationToken ct)
        => (await _db.TrainingDatasets.Where(d => d.ExperimentId == experimentId && d.Type == type).MaxAsync(d => (int?)d.Version, ct) ?? 0) + 1;

    private static string CodeFor(TrainingDatasetType type, int version) => $"{type.ToString().ToUpperInvariant()}-v{version}";

    private async Task EnsureSelectionPhaseAsync(int experimentId, CancellationToken ct)
    {
        var status = await _db.Experiments.Where(e => e.Id == experimentId).Select(e => e.Status).FirstAsync(ct);
        if (status is not (ExperimentStatus.PreTrainingClosed or ExperimentStatus.DatasetSelection))
            throw new ResearchValidationException("err.dataset.selection_phase_required");
    }

    /// <summary>Executes a selection rule and stores the result as a new AESTHETIC dataset version. The rule is frozen.</summary>
    public async Task<TrainingDataset> CreateAestheticAsync(int experimentId, int ruleId, CancellationToken ct = default)
    {
        await EnsureSelectionPhaseAsync(experimentId, ct);
        var rule = await _selection.GetAsync(experimentId, ruleId, ct);
        var def = Json.Deserialize<SelectionRuleDefinition>(rule.RuleJson);
        var preview = await _selection.PreviewAsync(experimentId, def, ct);
        var selected = preview.Rows.Where(r => r.Selected).ToList();
        if (selected.Count == 0) throw new ResearchValidationException("err.selection.empty");

        if (!rule.IsFrozen) await _selection.FreezeAsync(experimentId, rule.Id, ct);
        var version = await NextVersionAsync(experimentId, TrainingDatasetType.Aesthetic, ct);
        var ds = new TrainingDataset
        {
            ExperimentId = experimentId,
            Type = TrainingDatasetType.Aesthetic,
            Version = version,
            Code = CodeFor(TrainingDatasetType.Aesthetic, version),
            Name = $"Aesthetic dataset v{version} ({rule.Name} v{rule.Version})",
            SelectionRuleId = rule.Id,
            Notes = preview.PercentileCutoff is { } c ? $"percentile cutoff {c:0.###}; eligible images {preview.Eligible}" : $"eligible images {preview.Eligible}"
        };
        int order = 0;
        foreach (var r in selected) ds.Items.Add(new TrainingDatasetItem { ImageAssetId = r.Image.ImageAssetId, Reason = r.Reason, SortOrder = order++ });
        _db.TrainingDatasets.Add(ds);
        await _db.SaveChangesAsync(ct);
        _audit.Add(experimentId, AuditActions.DatasetGenerated, nameof(TrainingDataset), ds.Id, after: new { ds.Code, ds.SelectionRuleId, Items = ds.Items.Count, Images = selected.Select(s => s.Image.ImageCode) });
        await _db.SaveChangesAsync(ct);
        return ds;
    }

    /// <summary>Creates a CONTROL dataset with the same size as the reference dataset, reproducible from the stored seed.</summary>
    public async Task<TrainingDataset> CreateControlAsync(int experimentId, ControlRequest req, CancellationToken ct = default)
    {
        await EnsureSelectionPhaseAsync(experimentId, ct);
        var reference = await GetAsync(experimentId, req.ReferenceDatasetId, ct);
        var variables = req.Variables.Where(v => MatchingVariables.Contains(v)).Distinct().ToList();
        if (req.Method != ControlSelectionMethod.Random && variables.Count == 0) throw new ResearchValidationException("err.control.variables_required");
        var seed = req.Seed is > 0 ? req.Seed.Value : DeterministicRandom.NewSeed();
        var pool = await _db.ImageAssets.AsNoTracking().Where(i => i.ExperimentId == experimentId && i.IsActive).OrderBy(i => i.Id).ToListAsync(ct);
        var referenceImages = reference.Items.Select(i => i.ImageAsset!).ToList();
        if (req.ExcludeReferenceImages)
        {
            var refIds = referenceImages.Select(i => i.Id).ToHashSet();
            pool = pool.Where(i => !refIds.Contains(i.Id)).ToList();
        }
        if (pool.Count < referenceImages.Count) throw new ResearchValidationException("err.control.pool_too_small", pool.Count, referenceImages.Count);

        var picked = SampleControl(pool, referenceImages, req.Method, variables, seed);
        var version = await NextVersionAsync(experimentId, TrainingDatasetType.Control, ct);
        var ds = new TrainingDataset
        {
            ExperimentId = experimentId,
            Type = TrainingDatasetType.Control,
            Version = version,
            Code = CodeFor(TrainingDatasetType.Control, version),
            Name = $"Control dataset v{version} ({req.Method}, ref {reference.Code})",
            RandomSeed = seed,
            ControlMethod = req.Method,
            MatchingVariables = string.Join(",", variables),
            ReferenceDatasetId = reference.Id,
            ExcludedReferenceImages = req.ExcludeReferenceImages,
            Notes = req.ExcludeReferenceImages ? "reference images excluded from pool" : "sampled from the whole active corpus (no aesthetic criterion)"
        };
        int order = 0;
        foreach (var (img, reason) in picked) ds.Items.Add(new TrainingDatasetItem { ImageAssetId = img.Id, Reason = reason, SortOrder = order++ });
        _db.TrainingDatasets.Add(ds);
        await _db.SaveChangesAsync(ct);
        _audit.Add(experimentId, AuditActions.DatasetGenerated, nameof(TrainingDataset), ds.Id,
            after: new { ds.Code, Method = req.Method.ToString(), ds.RandomSeed, ds.MatchingVariables, ds.ExcludedReferenceImages, Reference = reference.Code, Images = picked.Select(p => p.Image.ImageCode) });
        await _db.SaveChangesAsync(ct);
        return ds;
    }

    public static string AspectBucket(ImageAsset a)
    {
        var r = a.AspectRatio;
        return r < 0.9 ? "portrait" : r <= 1.1 ? "square" : r <= 1.6 ? "landscape" : "wide";
    }

    public static string VariableValue(ImageAsset a, string variable) => (variable switch
    {
        "BuildingType" => a.BuildingType,
        "Period" => a.Period,
        "Country" => a.Country,
        "Continent" => a.Continent,
        "Style" => a.ArchitecturalStyle,
        "IndustrialOrNonIndustrial" => a.IndustrialOrNonIndustrial,
        "AspectRatio" => AspectBucket(a),
        _ => null
    }) ?? "∅";

    private static string StratumKey(ImageAsset a, IReadOnlyList<string> vars) => string.Join(" | ", vars.Select(v => $"{v}={VariableValue(a, v)}"));

    /// <summary>
    /// Deterministic control sampling (pure function, unit-tested).
    /// Random: simple random sample. StratifiedRandom: proportional allocation to the strata of the pool (largest remainder).
    /// MatchedControl: reproduces the stratum counts of the reference dataset; when a stratum has too few images the last
    /// matching variable is relaxed progressively, then the remainder is filled at random. Every item records why it was chosen.
    /// </summary>
    public static List<(ImageAsset Image, string Reason)> SampleControl(IReadOnlyList<ImageAsset> pool, IReadOnlyList<ImageAsset> reference, ControlSelectionMethod method, IReadOnlyList<string> variables, int seed)
    {
        var rng = new DeterministicRandom(seed);
        var n = reference.Count;
        var available = pool.OrderBy(i => i.Id).ToList();
        rng.Shuffle(available);
        var result = new List<(ImageAsset, string)>();
        var used = new HashSet<int>();

        void Take(IEnumerable<ImageAsset> candidates, int count, string reason)
        {
            foreach (var c in candidates)
            {
                if (count <= 0) break;
                if (used.Add(c.Id)) { result.Add((c, reason)); count--; }
            }
        }

        switch (method)
        {
            case ControlSelectionMethod.Random:
                Take(available, n, $"random (seed {seed})");
                break;

            case ControlSelectionMethod.StratifiedRandom:
            {
                var strata = available.GroupBy(i => StratumKey(i, variables)).OrderBy(g => g.Key, StringComparer.Ordinal).ToList();
                var quotas = strata.Select(g => (g.Key, Exact: (double)g.Count() * n / available.Count)).ToList();
                var alloc = quotas.ToDictionary(q => q.Key, q => (int)Math.Floor(q.Exact));
                var remainder = n - alloc.Values.Sum();
                foreach (var q in quotas.OrderByDescending(q => q.Exact - Math.Floor(q.Exact)).ThenBy(q => q.Key, StringComparer.Ordinal).Take(remainder))
                    alloc[q.Key]++;
                foreach (var g in strata) Take(g, alloc[g.Key], $"stratified: {g.Key}");
                Take(available, n - result.Count, "stratified: fill");
                break;
            }

            case ControlSelectionMethod.MatchedControl:
            {
                var targets = reference.GroupBy(i => StratumKey(i, variables)).OrderBy(g => g.Key, StringComparer.Ordinal).ToList();
                var deficits = new List<(ImageAsset Ref, int Missing)>();
                foreach (var t in targets)
                {
                    var need = t.Count();
                    var matches = available.Where(i => StratumKey(i, variables) == t.Key).ToList();
                    var before = result.Count;
                    Take(matches, need, $"matched: {t.Key}");
                    var got = result.Count - before;
                    if (got < need) deficits.Add((t.First(), need - got));
                }
                // relax variables from the last one
                for (int k = variables.Count - 1; k >= 1 && deficits.Count > 0; k--)
                {
                    var subset = variables.Take(k).ToList();
                    var next = new List<(ImageAsset, int)>();
                    foreach (var (refImg, missing) in deficits)
                    {
                        var key = StratumKey(refImg, subset);
                        var before = result.Count;
                        Take(available.Where(i => StratumKey(i, subset) == key), missing, $"matched (relaxed to {string.Join(",", subset)}): {key}");
                        var got = result.Count - before;
                        if (got < missing) next.Add((refImg, missing - got));
                    }
                    deficits = next;
                }
                Take(available, n - result.Count, "matched: random fill");
                break;
            }
        }
        return result;
    }

    /// <summary>
    /// Freezes a dataset. Every image must have an approved (reviewed) current caption without forbidden terms.
    /// Caption texts are snapshotted into the dataset items so that exports stay identical forever.
    /// </summary>
    public async Task FreezeAsync(int experimentId, int id, CancellationToken ct = default)
    {
        var ds = await GetAsync(experimentId, id, ct);
        if (ds.IsFrozen) return;
        var experiment = await _db.Experiments.FirstAsync(e => e.Id == experimentId, ct);
        var cfg = ExperimentService.GetConfiguration(experiment);
        var missing = ds.Items.Count(i => CaptionService.CurrentOf(i.ImageAsset!) is not { Reviewed: true });
        if (missing > 0) throw new ResearchValidationException("err.freeze.captions_missing", missing);
        var forbidden = ds.Items.Count(i => CaptionService.FindForbiddenTerms(CaptionService.CurrentOf(i.ImageAsset!)!.Text, cfg.ForbiddenCaptionTerms).Count > 0);
        if (forbidden > 0) throw new ResearchValidationException("err.freeze.captions_forbidden", forbidden);
        if (ds.Items.Count == 0) throw new ResearchValidationException("err.dataset.empty");
        foreach (var item in ds.Items)
        {
            var cap = CaptionService.CurrentOf(item.ImageAsset!)!;
            item.CaptionId = cap.Id;
            item.CaptionText = cap.Text;
        }
        ds.IsFrozen = true;
        ds.FrozenAt = DateTime.UtcNow;
        _audit.Add(experimentId, AuditActions.DatasetFrozen, nameof(TrainingDataset), ds.Id, after: new { ds.Code, Items = ds.Items.Count });
        await _db.SaveChangesAsync(ct);
    }

    /// <summary>Creates an unfrozen copy (version + 1) of a dataset, keeping lineage.</summary>
    public async Task<TrainingDataset> NewVersionAsync(int experimentId, int id, string? reason, CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(reason)) throw new ResearchValidationException("err.reason_required");
        var src = await GetAsync(experimentId, id, ct);
        var version = await NextVersionAsync(experimentId, src.Type, ct);
        var ds = new TrainingDataset
        {
            ExperimentId = experimentId, Type = src.Type, Version = version, Code = CodeFor(src.Type, version),
            Name = $"{src.Type} dataset v{version} (from {src.Code})", SelectionRuleId = src.SelectionRuleId, RandomSeed = src.RandomSeed,
            ControlMethod = src.ControlMethod, MatchingVariables = src.MatchingVariables, ReferenceDatasetId = src.ReferenceDatasetId,
            ExcludedReferenceImages = src.ExcludedReferenceImages, PreviousVersionId = src.Id, Notes = $"new version of {src.Code}: {reason.Trim()}"
        };
        foreach (var i in src.Items.OrderBy(i => i.SortOrder)) ds.Items.Add(new TrainingDatasetItem { ImageAssetId = i.ImageAssetId, Reason = i.Reason, SortOrder = i.SortOrder });
        // a new CONTROL version follows a newer AESTHETIC version that contains exactly the same images (e.g. only the captions changed):
        // the matching is still valid, so the control points to the version that will actually be trained
        if (src.Type == TrainingDatasetType.Control && src.ReferenceDatasetId is { } oldRef)
        {
            var refs = await _db.TrainingDatasets.AsNoTracking().Include(d => d.Items)
                .Where(d => d.ExperimentId == experimentId && d.Type == TrainingDatasetType.Aesthetic && d.IsFrozen).ToListAsync(ct);
            var old = refs.FirstOrDefault(d => d.Id == oldRef);
            var latest = refs.MaxBy(d => d.Version);
            if (old != null && latest != null && latest.Id != old.Id
                && latest.Items.Select(i => i.ImageAssetId).ToHashSet().SetEquals(old.Items.Select(i => i.ImageAssetId)))
                ds.ReferenceDatasetId = latest.Id;
        }
        _db.TrainingDatasets.Add(ds);
        await _db.SaveChangesAsync(ct);
        _audit.Add(experimentId, AuditActions.DatasetGenerated, nameof(TrainingDataset), ds.Id, after: new { ds.Code, From = src.Code }, reason: reason);
        await _db.SaveChangesAsync(ct);
        return ds;
    }

    /// <summary>Manual edit of an unfrozen dataset (add/remove one image) with mandatory reason.</summary>
    public async Task SetMembershipAsync(int experimentId, int id, int imageAssetId, bool include, string? reason, CancellationToken ct = default)
    {
        if (string.IsNullOrWhiteSpace(reason)) throw new ResearchValidationException("err.reason_required");
        var ds = await GetAsync(experimentId, id, ct);
        if (ds.IsFrozen) throw new FrozenException("err.dataset.frozen", ds.Code);
        var item = ds.Items.FirstOrDefault(i => i.ImageAssetId == imageAssetId);
        if (include && item == null)
        {
            var img = await _db.ImageAssets.FirstOrDefaultAsync(i => i.Id == imageAssetId && i.ExperimentId == experimentId, ct) ?? throw new NotFoundException(nameof(ImageAsset), imageAssetId);
            ds.Items.Add(new TrainingDatasetItem { ImageAssetId = img.Id, Reason = $"manual: {reason.Trim()}", SortOrder = ds.Items.Count == 0 ? 0 : ds.Items.Max(i => i.SortOrder) + 1 });
        }
        else if (!include && item != null) ds.Items.Remove(item);
        else return;
        _audit.Add(experimentId, AuditActions.ManualCorrection, nameof(TrainingDataset), ds.Id, after: new { ImageAssetId = imageAssetId, Include = include }, reason: reason);
        await _db.SaveChangesAsync(ct);
    }

    /// <summary>Administrator-only escape hatch: unfreezes a dataset with a documented reason (audited). Prefer <see cref="NewVersionAsync"/>.</summary>
    public async Task UnfreezeOverrideAsync(int experimentId, int id, string? reason, bool isAdministrator, CancellationToken ct = default)
    {
        if (!isAdministrator) throw new ResearchValidationException("err.admin_only");
        if (string.IsNullOrWhiteSpace(reason)) throw new ResearchValidationException("err.reason_required");
        var ds = await GetAsync(experimentId, id, ct);
        if (!ds.IsFrozen) return;
        if (await _db.TrainingRuns.AnyAsync(r => r.TrainingDatasetId == ds.Id, ct)) throw new ResearchValidationException("err.dataset.used_by_training_run");
        ds.IsFrozen = false;
        ds.FrozenAt = null;
        _audit.Add(experimentId, AuditActions.DatasetUnfreezeOverride, nameof(TrainingDataset), ds.Id, new { IsFrozen = true }, new { IsFrozen = false }, reason);
        await _db.SaveChangesAsync(ct);
    }
}
