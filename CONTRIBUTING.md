# Contributing

Contributions are welcome for design corrections, clearer documentation, and new workshop tools that fit the purpose of this repository.

## Design workflow

1. Open the relevant `.FCStd` source in FreeCAD.
2. Make the smallest clearly scoped change needed.
3. Save the source and record the change in the design README or revision notes.
4. Regenerate the published exports that are affected by the change.
5. Inspect the source and at least one exported file after reopening or importing them.
6. Update documentation when dimensions, intended use, materials, compatibility, or limitations change.

Do not treat an `.FCBak` file as the canonical source. Keep the primary `.FCStd` file identifiable and avoid committing editor-generated temporary files.

## Naming and layout

- Use a descriptive, lowercase directory name for each design.
- Keep the editable FreeCAD source in the design directory.
- Keep published interchange files in an `exports/` subdirectory, grouped by variant when necessary.
- Keep an `README.md` in each design directory.
- Use the [design documentation template](docs/design-documentation-template.md) for new designs.

Preserve existing filenames when updating an established export package unless there is a clear compatibility reason to change them. If a filename or directory changes, document the change.

## Documentation standards

Document only verified facts. Record units, dimensions, tolerances, material recommendations, and machine compatibility only when they are known and identify their source when useful. Clearly label assumptions and values that still need verification.

Design documentation should include the intended use, file map, fabrication/use checks, limitations, and revision notes. Avoid presenting an unvalidated design as certified tooling or safety equipment.

## Review checklist

Before opening a pull request or sharing an update, check that:

- The FreeCAD source opens without errors.
- Affected STEP, STL, OBJ, and MTL exports are present and importable where applicable.
- Exported files match the intended source and variant.
- Documentation links and file paths are valid.
- No private, temporary, or machine-generated files are included.
- The change respects the repository license.

## License

By contributing, you agree that your contribution can be distributed under the repository terms in [`LICENSE.md`](LICENSE.md). Contributions must not remove or weaken the existing attribution, non-commercial, or no-derivatives requirements without an explicit licensing decision from the project owner.
