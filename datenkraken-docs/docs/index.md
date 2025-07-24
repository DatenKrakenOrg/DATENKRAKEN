# DATENKRAKEN

## Commands

* `mkdocs new [dir-name]` - Create a new project.
* `mkdocs serve` - Start the live-reloading docs server.
* `mkdocs build` - Build the documentation site.
* `mkdocs -h` - Print help message and exit.

## Project layout

    mkdocs.yml    # The configuration file.
    docs/
        index.md  # The documentation homepage.
        arc42/    # Arc42
            images/ # Images used within - Make sure you use the same naming
            ..
        se/       # Software Engineering related documentation in full length. Use this folder to store your referenced in depth docs in arc42.
            re/   # Requirements-Engineering related
                ..

## ARC42 Template
ARC42 Template taken from public repo: <a href="https://github.com/NetworkedAssets/arc42-in-markdown-template/tree/master">Take a look here</a>

Thanks to you!

## AI Usage
Within the documentation we collectively use foundation models to generate blueprints of html tables. <b>Foundation models weren't instructed to generate the actual informative content of each table! Instead it's only used to reduce the workload of repetitive tasks (e.g. enumerations, html syntax, etc.).</b>
