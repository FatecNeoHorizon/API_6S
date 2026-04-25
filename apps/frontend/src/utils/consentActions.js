export function buildConsentActions({
  mandatoryClauses,
  optionalClauses,
  selectedOptionalIds,
}) {
  const mandatoryActions = mandatoryClauses.map((clause) => ({
    clause_uuid: clause.clause_uuid,
    policy_version_id: clause.policy_version_id,
    action: "CONSENT",
  }));

  const optionalActions = optionalClauses.map((clause) => ({
    clause_uuid: clause.clause_uuid,
    policy_version_id: clause.policy_version_id,
    action: selectedOptionalIds.has(clause.clause_uuid)
      ? "CONSENT"
      : "REVOCATION",
  }));

  return [...mandatoryActions, ...optionalActions];
}