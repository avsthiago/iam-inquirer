from typing import Dict, List
from rich.console import Console
from rich.progress import track
import boto3
import json
from rich import print_json


class AWSIamInteractor:
    def __init__(self, role_name: str, verbose: bool = False) -> None:
        self.console = Console()
        self.verbose = verbose
        self.iam = boto3.client("iam")
        self.role_name = role_name
        self.role = self._get_role(self.role_name)
        self.policies = self._get_role_policies(self.role_name)
        self.role_with_policies = self._create_role_with_policies(
            self.role, self.policies
        )

    def _create_role_with_policies(
        self, role: Dict[str, str], policies: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        role_with_policies = role.copy()
        role_with_policies["Policies"] = policies.copy()
        return role_with_policies

    def _get_role(self, role_name: str) -> Dict[str, str]:
        with self.console.status("[bold]Fetching role..."):
            role = self.iam.get_role(RoleName=role_name)
            role = self._filter_role_attributes(role["Role"])
        self._console_print("[bold green]Role fetched.")
        return role

    def _filter_role_attributes(
        self, role: Dict[str, str], keys: List[str] = None
    ) -> Dict[str, any]:
        default_keys = ["RoleName", "Arn", "Description"]
        keys = keys if keys is not None else default_keys
        return self._filter_attributes(role, keys)

    def _get_role_policies(self, role_name: str) -> List[Dict[str, str]]:
        attached_policies = self._get_attached_policies(role_name)
        policies = []
        for attached_policy in track(
            attached_policies, description="Downloading policies...", transient=True
        ):
            policy = self._add_description_and_version_to_policy(attached_policy)
            policy = self._add_policy_statement_to_policy(policy)
            policies.append(policy)
        self._console_print(
            f"[bold green]{len(attached_policies)} Policies downloaded."
        )
        return policies

    def _get_attached_policies(self, role_name: str) -> List[Dict[str, str]]:
        policy_paginator = self.iam.get_paginator("list_attached_role_policies")
        role_policies = []
        for response in policy_paginator.paginate(RoleName=role_name):
            role_policies.extend(response.get("AttachedPolicies"))
        return role_policies

    def _add_description_and_version_to_policy(
        self, attached_policy: Dict[str, str]
    ) -> Dict[str, str]:
        response = self.iam.get_policy(PolicyArn=attached_policy.get("PolicyArn"))
        policy = response.get("Policy")
        policy_extension = self._filter_attributes(
            policy, ["DefaultVersionId", "Description"]
        )
        return {**attached_policy, **policy_extension}

    def _add_policy_statement_to_policy(self, policy: Dict[str, str]) -> Dict[str, str]:
        policy_version = self.iam.get_policy_version(
            PolicyArn=policy.get("PolicyArn"), VersionId=policy.get("DefaultVersionId")
        )
        policy["Document"] = policy_version["PolicyVersion"]["Document"]["Statement"]
        return policy

    def _filter_attributes(
        self, dictionary: Dict[str, str], keys: List[str]
    ) -> Dict[str, str]:
        return {key: dictionary[key] for key in keys}

    def _console_print(self, message: str) -> None:
        if self.verbose:
            self.console.print(message)

    def show(self) -> None:
        self.role_with_policies["a"] = "[bold green] test"
        print_json(json.dumps(self.role_with_policies))

    def search(self) -> None:
        from rich.json import JSON

        json_renderable = JSON.from_data(
            json.dumps(self.role_with_policies),
            indent=2,
            highlight=False,
            skip_keys=False,
            ensure_ascii=True,
            check_circular=True,
            allow_nan=True,
            default=None,
            sort_keys=False,
        )
        print("a")
        roles = json.dumps(self.role_with_policies, indent=2)
        print("roles")
        from rich.text import Text

        tex = Text(json.dumps(self.role_with_policies, indent=2))
        tex.highlight_words(["List"], style="magenta")
        self.console.print(tex)


aws_iam_interactor = AWSIamInteractor("eksworkshop-admin")
aws_iam_interactor.search()
