# Tutorial notebook database

## Tips

### Clearing notebook output

Use the [`nbstripout`](https://github.com/kynan/nbstripout) tool.

### Regenerating tutorial notebook output for the documentation 

To execute a notebook from the command line, use
```bash
jupyter nbconvert --execute --to notebook --inplace <my_notebook>
```
This works with wildcards, meaning that 
```bash
jupyter nbconvert --execute --to notebook --inplace **/*.ipynb
```
will do so for all `.ipynb` files in all subdirectories.