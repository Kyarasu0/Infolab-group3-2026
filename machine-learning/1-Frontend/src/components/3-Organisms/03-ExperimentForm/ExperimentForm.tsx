import type { EvaluationPlan, ParameterDescriptions } from "@/functions/api-types";
import { Button } from "../../1-Atoms/01-Button/Button";
import { Panel } from "../../1-Atoms/03-Panel/Panel";
import { ParameterField } from "../../2-Molecules/04-ParameterField/ParameterField";
import styles from "./ExperimentForm.module.css";

interface ExperimentFormProps {
  scenarioNames: string[];
  scenarioName: string;
  onScenarioChange: (name: string) => void;
  plans: EvaluationPlan[];
  planName: string;
  onPlanChange: (name: string) => void;
  descriptions: ParameterDescriptions;
  parameterTexts: Record<string, Record<string, string>>;
  onParameterChange: (model: string, key: string, text: string) => void;
  note: string;
  onNoteChange: (note: string) => void;
  canRun: boolean;
  onRun: () => void;
}

export function ExperimentForm(props: ExperimentFormProps) {
  const planDescription = props.plans.find((plan) => plan.name === props.planName)?.description;
  return (
    <Panel>
      <h2>実験(評価して記録する)</h2>
      <p className={styles.note}>
        シナリオ・評価計画・パラメータを選んで評価し、結果を記録します。同じ条件の記録があるときは、過去の結果を表示するか、もう一度実行するかを選べます。
      </p>
      <div className={styles.selectors}>
        <label className={styles.selector}>
          シナリオ
          <select value={props.scenarioName} onChange={(event) => props.onScenarioChange(event.target.value)}>
            {props.scenarioNames.map((name) => <option key={name} value={name}>{name}</option>)}
          </select>
        </label>
        <label className={styles.selector}>
          評価計画
          <select value={props.planName} onChange={(event) => props.onPlanChange(event.target.value)}>
            {props.plans.map((plan) => <option key={plan.name} value={plan.name}>{plan.name}</option>)}
          </select>
          <span className={styles.hint}>{planDescription}</span>
        </label>
      </div>

      {Object.entries(props.parameterTexts).map(([model, values]) => (
        <fieldset key={model} className={styles.group}>
          <legend>{props.descriptions[model]?.model.label ?? model}</legend>
          <p className={styles.hint}>{props.descriptions[model]?.model.description}</p>
          <div className={styles.fields}>
            {Object.entries(values).map(([key, text]) => {
              const description = props.descriptions[model]?.parameters[key];
              return (
                <ParameterField key={key} name={key} label={description?.label ?? key}
                  description={description?.description} text={text}
                  onChange={(nextText) => props.onParameterChange(model, key, nextText)} />
              );
            })}
          </div>
        </fieldset>
      ))}

      <ParameterField label="メモ" description="この実験の目的や気づきを、自由に書き残せる(記録に保存される)" text={props.note} onChange={props.onNoteChange} />
      <Button primary disabled={!props.canRun} onClick={props.onRun}>評価して記録する</Button>
    </Panel>
  );
}
