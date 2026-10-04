namespace AestheticArchitectureResearch.Application.Common;

/// <summary>
/// Deterministic, platform-independent pseudo-random generator (xoshiro256** seeded with SplitMix64).
/// Used for every randomization in the protocol so that sequences can be regenerated from the stored seed
/// independently of the .NET runtime version (System.Random does not guarantee cross-version stability).
/// </summary>
public sealed class DeterministicRandom
{
    private ulong _s0, _s1, _s2, _s3;

    public DeterministicRandom(long seed)
    {
        ulong x = unchecked((ulong)seed);
        _s0 = SplitMix64(ref x);
        _s1 = SplitMix64(ref x);
        _s2 = SplitMix64(ref x);
        _s3 = SplitMix64(ref x);
    }

    private static ulong SplitMix64(ref ulong x)
    {
        ulong z = unchecked(x += 0x9E3779B97F4A7C15UL);
        z = unchecked((z ^ (z >> 30)) * 0xBF58476D1CE4E5B9UL);
        z = unchecked((z ^ (z >> 27)) * 0x94D049BB133111EBUL);
        return z ^ (z >> 31);
    }

    private static ulong Rotl(ulong x, int k) => (x << k) | (x >> (64 - k));

    public ulong NextUInt64()
    {
        ulong result = unchecked(Rotl(_s1 * 5, 7) * 9);
        ulong t = _s1 << 17;
        _s2 ^= _s0;
        _s3 ^= _s1;
        _s1 ^= _s2;
        _s0 ^= _s3;
        _s2 ^= t;
        _s3 = Rotl(_s3, 45);
        return result;
    }

    /// <summary>Uniform integer in [0, maxExclusive) without modulo bias (Lemire rejection).</summary>
    public int NextInt(int maxExclusive)
    {
        if (maxExclusive <= 0) throw new ArgumentOutOfRangeException(nameof(maxExclusive));
        ulong bound = (ulong)maxExclusive;
        ulong threshold = (0UL - bound) % bound;
        while (true)
        {
            ulong r = NextUInt64();
            if (r >= threshold) return (int)(r % bound);
        }
    }

    /// <summary>Uniform double in [0, 1).</summary>
    public double NextDouble() => (NextUInt64() >> 11) * (1.0 / (1UL << 53));

    public bool NextBool() => (NextUInt64() >> 63) == 1;

    /// <summary>In-place Fisher–Yates shuffle.</summary>
    public void Shuffle<T>(IList<T> list)
    {
        for (int i = list.Count - 1; i > 0; i--)
        {
            int j = NextInt(i + 1);
            (list[i], list[j]) = (list[j], list[i]);
        }
    }

    /// <summary>Creates a new cryptographically random 31-bit seed (positive int for portability).</summary>
    public static int NewSeed() => System.Security.Cryptography.RandomNumberGenerator.GetInt32(1, int.MaxValue);
}
