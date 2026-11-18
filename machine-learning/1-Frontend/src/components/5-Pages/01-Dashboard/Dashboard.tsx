// 画面全体(1枚): ヘッダー → 実行状況 → シナリオ → 実験 → 記録 → 比較と学習曲線 → 散布図と誤差の分布 → データの概要 → モデルの構成
import { useMemo } from "react";

import modes from "@shared/concept/modes.json";
import { bind } from "@/functions/cx";
import layout from "@/styles/layout.module.css";
import { Panel } from "../../1-Atoms/03-Panel/Panel";
import { LineChart } from "../../2-Molecules/02-LineChart/LineChart";
import { ArchitectureViewer } from "../../3-Organisms/02-ArchitectureViewer/ArchitectureViewer";
import { CompareChart } from "../../3-Organisms/07-CompareChart/CompareChart";
import { ExistingRecordNotice } from "../../3-Organisms/05-ExistingRecordNotice/ExistingRecordNotice";
import { ExperimentForm } from "../../3-Organisms/03-ExperimentForm/ExperimentForm";
import { RecordHistory } from "../../3-Organisms/04-RecordHistory/RecordHistory";
import { RunStatus } from "../../3-Organisms/06-RunStatus/RunStatus";
import { DataSummary } from "../../3-Organisms/10-DataSummary/DataSummary";
import { ErrorDistributionPanel } from "../../3-Organisms/09-ErrorDistributionPanel/ErrorDistributionPanel";
import { ScatterPanel } from "../../3-Organisms/08-ScatterPanel/ScatterPanel";
import { ScenarioPanel } from "../../3-Organisms/01-ScenarioPanel/ScenarioPanel";
import { AppHeader } from "../../4-Templates/01-AppHeader/AppHeader";
import styles from "./Dashboard.module.css";
import { useDashboard } from "./useDashboard";
import { useExperiments } from "./useExperiments";
import { useVisuals } from "./useVisuals";

const cx = bind(layout, styles);

export function Dashboard() {
  const dashboard = useDashboard();
  const scenarioNames = useMemo(() => dashboard.scenarios.map((scenario) => scenario.name), [dashboard.scenarios]);
  const experiments = useExperiments(scenarioNames, dashboard.job, dashboard.refreshJob, dashboard.setErrorMessage);
  const visuals = useVisuals(dashboard.selectedName, dashboard.scenarios, dashboard.job);
  const isTrainMode = dashboard.mode === "train";

  // 学習中は進捗の損失、そうでなければ選んだシナリオの学習曲線を見せる
  const isTraining = dashboard.job.state === "running";
  const lossValues = isTraining ? dashboard.job.autoencoder_loss : dashboard.result?.history.autoencoder_loss ?? [];
  const lossTitle = isTraining ? `学習中: ${dashboard.job.scenario}` : `学習曲線: ${dashboard.selectedName ?? "シナリオ未選択"}`;

  return (
    <>
      <AppHeader
        modeLabel={modes.find((mode) => mode.name === dashboard.mode)?.label ?? dashboard.mode}
        isTrainMode={isTrainMode}
        canSwitch={!dashboard.isBusy}
        onSwitch={() => dashboard.switchMode(isTrainMode ? "predict" : "train")}
      />
      <main className={cx("page", "stack")}>
        {dashboard.errorMessage && <p className={cx("error")}>{dashboard.errorMessage}</p>}
        <RunStatus job={dashboard.job} />
        <ScenarioPanel scenarios={dashboard.scenarios} mode={dashboard.mode} isBusy={dashboard.isBusy}
          selectedName={dashboard.selectedName} onSelect={dashboard.select} onTrain={dashboard.train} onCompare={dashboard.compare} />
        <ExperimentForm
          scenarioNames={scenarioNames} scenarioName={experiments.scenarioName} onScenarioChange={experiments.setScenarioName}
          plans={experiments.plans} planName={experiments.planName} onPlanChange={experiments.setPlanName}
          descriptions={experiments.descriptions} parameterTexts={experiments.parameterTexts}
          onParameterChange={experiments.changeParameter} note={experiments.note} onNoteChange={experiments.setNote}
          canRun={isTrainMode && !dashboard.isBusy && experiments.scenarioName !== ""} onRun={experiments.runExperiment} />
        {experiments.existingRecord && (
          <ExistingRecordNotice record={experiments.existingRecord} onShowRecord={experiments.showExistingRecord}
            onRerun={experiments.rerunExperiment} onClose={experiments.closeNotice} />
        )}
        <RecordHistory records={experiments.records} selectedId={experiments.selectedRecordId}
          onSelect={experiments.setSelectedRecordId} detail={experiments.recordDetail} />
        <div className={cx("grid2")}>
          <CompareChart records={experiments.records} planName={experiments.planName} />
          <Panel>
            <LineChart title={lossTitle} xLabel="エポック " format={(value) => value.toFixed(4)}
              series={[{ name: "損失", color: "var(--chart-1)", values: lossValues }]} />
          </Panel>
        </div>
        <div className={cx("grid2")}>
          <ScatterPanel scenarioName={dashboard.selectedName} scatter={visuals.scatter.data} message={visuals.scatter.message} />
          <ErrorDistributionPanel scenarioName={dashboard.selectedName} distribution={visuals.errorDistribution.data}
            message={visuals.errorDistribution.message} />
        </div>
        <DataSummary summary={visuals.dataSummary.data} message={visuals.dataSummary.message} />
        <ArchitectureViewer architecture={dashboard.architecture} />
      </main>
    </>
  );
}
