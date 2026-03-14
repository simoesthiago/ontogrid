import { CopilotClient } from "./copilot-client";
import { getQueryValue } from "../../lib/energy-hub";

export default async function CopilotPage({
  searchParams,
}: {
  searchParams: Promise<Record<string, string | string[] | undefined>>;
}) {
  const resolvedSearchParams = await searchParams;
  const datasetId = getQueryValue(resolvedSearchParams.dataset)?.trim();
  const entityId = getQueryValue(resolvedSearchParams.entity)?.trim();

  return (
    <div className="pageWorkspace">
      <div className="pageTitleBar">
        <h1 className="pageTitle">Copilot</h1>
      </div>

      <CopilotClient datasetId={datasetId} entityId={entityId} />
    </div>
  );
}
