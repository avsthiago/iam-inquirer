from InquirerPy import inquirer
from InquirerPy.base.control import Choice
import typer
import iam_inquirer


app = typer.Typer()
state = {"verbose": False}


@app.command()
def search(role_name: str):
    pass


@app.command()
def show(role_name: str):
    iam_inquirer.AWSIamInteractor(role_name=role_name).show()


def search_menu():
    pass


@app.callback()
def main(verbose: bool = False):
    """
    Manage users in the awesome CLI app.
    """
    if verbose:
        print("Will write verbose output")
        state["verbose"] = True


if __name__ == "__main__":
    app()
