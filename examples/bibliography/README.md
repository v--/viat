# Bibliography management

Over the years, I gradually crated my own [BibLaTeX manager](https://github.com/v--/notebook#biblatex-tools), which helps me maintain consistency in `.bib` files. Viat's programmatic API helps me connect bib entries with actual files. I will present a very cut-down version of what I actually use since my script is made to manage hundreds of diverse files.

As an example, I will use the [freely available](https://web.stanford.edu/~boyd/cvxbook/) book "Convex Optimization" by Boyd and Vandenberghe, provided here as the dummy file `Stephen Boyd, Lieven Vandenberghe - Convex Optimization.pdf`.

> [!TIP]
> See the [usage tutorial](https://viat.readthedocs.io/en/stable/usage/) for an outline of how Viat works.

The tracker is configured in [`.viat/config.toml`](./.viat/config.toml) as follows:

```toml
[tracker.glob]
patterns = ["*.{pdf,djvu,epub,fb2}"]
```

Thus, every e-book (in the aforementioned formats) will get tracked:

```console
$ viat tracked
Stephen Boyd, Lieven Vandenberghe - Convex Optimization.pdf
```

The actual metainformation for this file is stored in [`.viat/index.bib`](./.viat/index.bib), along with another mock entry:

```bibtex
@book{BoydVandenberghe2004ConvexOptimization,
  author = {Stephen P. Boyd and Lieven Vandenberghe},
  date = {2004-03-08},
  isbn = {978-0-521-83378-3},
  language = {english},
  publisher = {Cambridge University Press \& Assessment},
  title = {Convex Optimization},
  url = {https://web.stanford.edu/~boyd/cvxbook/}
}

@book{ValidRef,
  author = {Valid Author},
  date = {2345},
  title = {Valid Title}
}
```

For the sake of this example, the only metainformation attached to this book will be a reference to this entry. [`.viat/storage.toml`](./.viat/storage.toml) contains the following:

```toml
["Stephen Boyd, Lieven Vandenberghe - Convex Optimization.pdf"]
ref = "BoydVandenberghe2004ConvexOptimization"

["invalid.pdf"]
ref = "InvalidRef"
```

This is straightforward enough, but consistency has to be maintained. The script [`check_consistency.py`](./check_consistency.py) checks for three-way consistency between tracked files, files known to the Viat storage and BibTeX entries. Running the script in this directory, we get the following output:

```console
$ uv run --script check_consistency
No known file corresponds to the BibTeX ref 'ValidRef'.
Missing BibTeX ref InvalidRef for file 'invalid.pdf'.
The file 'invalid.pdf' has Viat metadata stored, but is not tracked by Viat.
```
