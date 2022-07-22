from typing import Dict, List
import boto3
import pprint


class AWSIamInteractor:
    def __init__(self, role_name: str) -> None:
        self.iam = boto3.client("iam")
        self.role_name = role_name
        self.role = self._get_role(self.role_name)
        self.policies = self._get_role_policies(self.role_name)
        self.role_with_policies = self._create_role_with_policies(
            self.role, self.policies
        )
        pprint.pprint(self.role_with_policies)

    def _create_role_with_policies(
        self, role: Dict[str, str], policies: List[Dict[str, str]]
    ) -> List[Dict[str, str]]:
        role_with_policies = role.copy()
        role_with_policies["Policies"] = policies.copy()
        return role_with_policies

    def _get_role(self, role_name: str) -> Dict[str, str]:
        role = self.iam.get_role(RoleName=role_name)
        return self._filter_role_attributes(role["Role"])

    def _filter_role_attributes(
        self, role: Dict[str, str], keys: List[str] = None
    ) -> Dict[str, any]:
        default_keys = ["RoleName", "Arn", "Description"]
        keys = keys if keys is not None else default_keys
        return self._filter_attributes(role, keys)

    def _get_role_policies(self, role_name: str) -> List[Dict[str, str]]:
        attached_policies = self._get_attached_policies(role_name)
        policies = []
        for attached_policy in attached_policies:
            policy = self._add_description_and_version_to_policy(attached_policy)
            policy = self._add_policy_statement_to_policy(policy)
            policies.append(policy)
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


aws_iam_interactor = AWSIamInteractor("eksworkshop-admin")
