# Native-tested Guardian / Forester fixture

`guardian_forester_forge.zip` is a byte-for-byte copy of the archive at
`samcnpc-behavior/src/test/resources/studio/guardian_forester.zip` in the canonical
SAMCNPC workspace at commit `b43112aeee24a76038674841294cb59433f82d8b`.
SHA-256: `a51404a573775aacd02cdc2b71ad0063e3305c136538d288a55067247d1f5b32`.

The real Forge loader and physical Guardian/Forester scenarios used this fixture
on 2026-09-28. See [the recorded evidence](../../examples/advanced/guardian_forester/VALIDATION.md).
This repository's GUI workflow checks document parity between the editable graph,
JSON, distributable ZIP and this independently preserved native fixture.
Changing a graph does not make a new export native-tested: repeat the corresponding
Forge checks before replacing the fixture and updating its provenance.

The older Guardian project used by the format-1 regression is bundled at
`tutorials/examples/complex_guardian_escort.samgraph` together with the GitHub tutorial
projects. Both tests run without a neighboring Minecraft/mod source checkout.
