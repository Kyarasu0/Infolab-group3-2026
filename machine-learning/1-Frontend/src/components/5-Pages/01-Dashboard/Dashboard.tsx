import { useMemo } from "react";

import { Button } from "../../1-Atoms/01-Button/Button";
import { StatusBadge } from "../../1-Atoms/02-StatusBadge/StatusBadge";
import { LossChart } from "../../2-Molecules/01-LossChart/LossChart";
import { ArchitectureViewer } from "../../3-Organisms/02-ArchitectureViewer/ArchitectureViewer";
import { ExperimentForm } from "../../3-Organisms/03-ExperimentForm/ExperimentForm";
import { RecordHistory } from "../../3-Organisms/04-RecordHistory/RecordHistory";
import { ExistingRecordNotice } from "../../3-Organisms/05-ExistingRecordNotice/ExistingRecordNotice";
import { ScenarioPanel } from "../../3-Organisms/01-ScenarioPanel/ScenarioPanel";
import styles from "./Dashboard.module.css";
import modes from "../../../../../3-Shared/concept/modes.json";
import { useDashboard } from "./useDashboard";
import { useExperiments } from "./useExperiments";

export function Dashboard() {
  const dashboard = useDashboard();
  const scenarioNames = useMemo(() => dashboard.scenarios.map((scenario) => scenario.name), [dashboard.scenarios]);
  const experiments = useExperiments(scenarioNames, dashboard.job, dashboard.refreshJob, dashboard.setErrorMessage);
  const { job, result } = dashboard;
  const isTrainMode = dashboard.mode === "train";

  // 学習中は進捗の損失、そうでなければ選んだシナリオの学習曲線を見せる
  const lossValues = job.state === "running" ? job.autoencoder_loss : result?.history.autoencoder_loss ?? [];
  const lossTitle = job.state === "running"
    ? `学習中: ${job.scenario}(エポック ${job.epoch})`
    : `学習曲線: ${dashboard.selectedName ?? "シナリオ未選択"}`;

  return (
    <main className={styles.page}>
      <header className={styles.header}>
        <h1 className={styles.title}>タイピング疲労・ストレス推定 ダッシュボード</h1>
        <div className={styles.modeSwitch}>
          <StatusBadge text={modes.find((mode) => mode.name === dashboard.mode)?.label ?? dashboard.mode} tone={isTrainMode ? "warning" : "success"} />
          <Button disabled={dashboard.isBusy} onClick={() => dashboard.switchMode(isTrainMode ? "predict" : "train")}>
            {isTrainMode ? "予測モードにする" : "学習モードにする"}
          </Button>
        </div>
      </header>

      {dashboard.errorMessage && <p className={styles.error}>{dashboard.errorMessage}</p>}
      {job.state === "failed" && <p className={styles.error}>学習に失敗しました: {job.error}</p>}

      <ScenarioPanel
        scenarios={dashboard.scenarios}
        mode={dashboard.mode}
        isBusy={dashboard.isBusy}
        selectedName={dashboard.selectedName}
        onSelect={dashboard.select}
        onTrain={dashboard.train}
        onCompare={dashboard.compare}
      />
      <ExperimentForm
        scenarioNames={scenarioNames}
        scenarioName={experiments.scenarioName}
        onScenarioChange={experiments.setScenarioName}
        plans={experiments.plans}
        planName={experiments.planName}
        onPlanChange={experiments.setPlanName}
        parameterTexts={experiments.parameterTexts}
        onParameterChange={experiments.changeParameter}
        note={experiments.note}
        onNoteChange={experiments.setNote}
        canRun={isTrainMode && !dashboard.isBusy && experiments.scenarioName !== ""}
        onRun={experiments.runExperiment}
      />
      {experiments.existingRecord && (
        <ExistingRecordNotice
          record={experiments.existingRecord}
          onShowRecord={experiments.showExistingRecord}
          onRerun={experiments.rerunExperiment}
          onClose={experiments.closeNotice}
        />
      )}
      <RecordHistory
        records={experiments.records}
        selectedId={experiments.selectedRecordId}
        onSelect={experiments.setSelectedRecordId}
        detail={experiments.recordDetail}
      />
      <LossChart title={lossTitle} values={lossValues} />
      <ArchitectureViewer architecture={dashboard.architecture} />
    </main>
  );
}
