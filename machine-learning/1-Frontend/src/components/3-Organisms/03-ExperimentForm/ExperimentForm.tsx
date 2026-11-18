import type { EvaluationPlan } from "../../../functions/api-types";
import { Button } from "../../1-Atoms/01-Button/Button";
import { ParameterField } from "../../2-Molecules/02-ParameterField/ParameterField";
import styles from "./ExperimentForm.module.css";

interface ExperimentFormProps {
  scenarioNames: string[];
  scenarioName: string;
  onScenarioChange: (name: string) => void;
  plans: EvaluationPlan[];
  planName: string;
  onPlanChange: (name: string) => void;
  parameterTexts: Record<string, Record<string, string>>;
  onParameterChange: (model: string, key: string, text: string) => void;
  note: string;
  onNoteChange: (note: string) => void;
  canRun: boolean;
  onRun: () => void;
}

export function ExperimentForm(props: ExperimentFormProps) {
  return (
    <section className={styles.form}>
      <h2 className={styles.title}>実験(評価して記録する)</h2>
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
            {props.plans.map((plan) => (
              <option key={plan.name} value={plan.name}>{plan.name}({plan.description})</option>
            ))}
          </select>
        </label>
      </div>

      {Object.entries(props.parameterTexts).map(([model, values]) => (
        <fieldset key={model} className={styles.group}>
          <legend>{model}</legend>
          <div className={styles.fields}>
            {Object.entries(values).map(([key, text]) => (
              <ParameterField key={key} label={key} text={text}
                onChange={(nextText) => props.onParameterChange(model, key, nextText)} />
            ))}
          </div>
        </fieldset>
      ))}

      <ParameterField label="メモ" text={props.note} onChange={props.onNoteChange} />
      <Button disabled={!props.canRun} onClick={props.onRun}>評価して記録する</Button>
    </section>
  );
}
