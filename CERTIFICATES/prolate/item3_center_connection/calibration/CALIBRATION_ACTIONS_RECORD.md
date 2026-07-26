# Centered calibration Actions record

## Source

- workflow run: `30209014310`
- source head: `78f1258bd444451f04f651a8b86160c33cd2d128`
- conclusion: **success**
- artifact: `prolate-item3-centered-calibration-final`
- artifact id: `8633908457`
- artifact ZIP SHA-256: `1df73fbe6a443ec09146e8593a579a59b41d76b9e9d15aacd894470658000329`
- strict JSON SHA-256: `39ea268b619eec144d50fa036aa0a465d3a764a9409f8c17cbfb76c2600f930b`

## Provenance

- base kernel SHA-256: `77e7a93c594ba66ac7d98df29ec3c03107b0c63962a5aa60f8503559082c10ac`
- F_rr extension SHA-256: `223b7007c9e077b204612fb1ff669b4147a2aa0f9c941cc8e83e81efd975e757`
- calibration harness SHA-256: `2398b6dad34117f2968b52cad31adb10d233aa9fa612afc3d09e1875ba61685f`
- endpoint canonicalizer SHA-256: `0b25bbe5ffe40f9ac7dca3b6b34918ce8cf78dd412cc3e8a99d4b27ee94425b1`

## Strict result

The common certified lower bound reconstructed from the stored endpoint pair is

```text
lower(abs(G'(m))) = [0.0206082997916417 +/- 4.88e-17].
```

| radius | rigorous C bound | rigorous slack bound | verdict |
|---|---|---|---|
| `1/256` | `[230.252185611054 +/- 3.02e-13]` | `[0.899422600043181 +/- 1.36e-16]` | false |
| `1/1024` | `[44.1738491151482 +/- 1.34e-14]` | `[0.0431385245265119 +/- 1.06e-18]` | false |
| `1/4096` | `[10.9041155967861 +/- 4.14e-14]` | `[0.00266213759687162 +/- 3.45e-18]` | **true** |

Thus cell width `1/2048` is accepted as the initial C-G-TUBE radial width.
This record certifies the calibration only; it does not certify C-G-TUBE.
