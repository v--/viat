```troff
VIAT(1)                               viat Manual                               VIAT(1)

NAME
     viat - A tool for managing virtual file attributes.

SYNOPSIS
     viat [OPTIONS] COMMAND [ARGS]...

DESCRIPTION
     A tool for managing virtual file attributes.

     In  short,  viat allows recording file attributes in a plain text file, by default
     TOML.

OPTIONS
     --version
            Show the version and exit.

COMMANDS
      viat get [OPTIONS] PATH ATTR

            Retrieve a stored attribute for a tracked file.

            Options:
            -r, --raw  Do not quote strings.
            --help     Show this message and exit.

      viat get-all [OPTIONS] PATH

            Retrieve all stored attributes for a tracked file.

            Options:
            --help  Show this message and exit.

      viat init [OPTIONS]

            Initialize a new vault.

            Options:
            --help  Show this message and exit.

      viat mv [OPTIONS] SRC DEST

            Move a file along with its metadata.

            Options:
            -f, --force  Move even if the destination exists.
            --help       Show this message and exit.

      viat rm [OPTIONS] PATH

            Remove a file along with its metadata.

            Options:
            --help  Show this message and exit.

      viat set [OPTIONS] PATH ATTR VALUE

            Update a stored attribute for a tracked file.

            Unless the --raw parameter is given, we treat the value as JSON.

            Options:
            -r, --raw  Treat the value like a string rather than as JSON.
            --help     Show this message and exit.

      viat stale [OPTIONS]

            Print out the paths with storage entries that are not tracked.

            Options:
            -j, --json  Print the list in JSON format.
            --help      Show this message and exit.

      viat tracked [OPTIONS]

            Print out the tracked file paths.

            Options:
            -j, --json     Print the list in JSON format.
            -n, --no-data  Print only those paths without any recorded attributes.
            --help         Show this message and exit.

      viat update [OPTIONS] PATH ATTRS

            Merge the stored attributes for a tracked file with a new JSON object.

            Options:
            --help  Show this message and exit.

ENVIRONMENT
     VIAT_DIR
            Use a concrete vault directory than searching through the current directory
            upwards.

TUTORIAL
     First, a vault must be initialized:

            viat init

     The vault is determined by a ".viat" subfolder  that  contains  "config.toml"  and
     "storage.toml" files (JSON is also supported for both). We can immediately set at-
     tributes for any file on the file system:

            $  viat  update  tractatus.pdf  '{"author":  "Ludwig Wittgenstein", "year":
            1921}'
            Warning: File 'tractatus.pdf' is not being tracked.
            {"author": "Ludwig Wittgenstein", "year": 1921}

     All stored attributes for the file get printed; in this case the only  stored  at-
     tributes  are  those  we  have  just  added. We also get a warning saying that the
     vault's tracker does not know about this file.

     The role of the tracker is to enumerate the files that are explicitly  tracked  by
     the vault. The default glob-based tracking provider requires explicit patterns. We
     can  track  all  PDF files in the root of the vault using the following configura-
     tion:

            [tracker.glob]
            patterns = ["*.pdf"]

     With this, we can add new properties without warnings:

            $ viat set tractatus.pdf rating 4
            {"author": "Ludwig Wittgenstein", "year": 1921, "rating": 4}

     The above worked because "true" is a valid JSON value; if we were to set a  string
     instead,  we would have to escape it in quotes, which is inconvenient. Instead, we
     can treat the value as a string by passing the "--raw" flag:

            $ viat set --raw tractatus.pdf publisher 'Annalen der Naturphilosophie'

     It  makes  sense  to  utilize  JSON  schemas.  Let  us  add   the   following   to
     ".viat/schema.json":

            {
              "type":"object",
              "properties": {
                "year": {"type": "number"}
              }
            }

     Now we can no longer set the year to anything that is not a number:

            $ viat set tractatus.pdf --raw year string
            Error: Validation error for 'tractatus.pdf': data.year must be number.

     The  essence  of  the tool is that the attributes are stored in plain text formats
     that can be edited committed to version control. For example, ".viat/storage.toml"
     should now look as follows:

            ["tractatus.pdf"]
            author = "Ludwig Wittgenstein"
            year = 1921
            rating = 4
            publisher = "Annalen der Naturphilosophie"

     If we manually change the year to "string", we will get a warning when loading the
     vault:

            $ viat get tractatus.pdf rating
            Warning: Validation error in stored  data  for  'tractatus.pdf':  data.year
            must be number.
            4

     If we move "tractatus.pdf" to "book.pdf", viat will no longer know about it:

            $ viat get book.pdf rating
            Warning: File 'book.pdf' is not being tracked.
            Error: Attribute 'rating' has not been set for 'book.pdf'.

     Such discrepancies can be determined relatively easily:

            $ viat stale
            tractatus.pdf
            $ viat tracked --no-data
            book.pdf

     For  such  cases,  we  provide  the helpers "viat mv" and "viat rm", but otherwise
     avoid being too clever.

0.9.0                                  2026-05-12                               VIAT(1)
```
