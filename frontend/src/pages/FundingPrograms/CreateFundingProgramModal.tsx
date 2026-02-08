import { useEffect, useState } from "react";
import {
  apiGet,
  apiPost,
  apiUploadFiles,
} from "../../utils/api";
import styles from "./FundingProgramsPage.module.css";

type TemplateList = {
  system: { id: string; name: string }[];
  user: { id: string; name: string }[];
};

export default function CreateFundingProgramModal({
  onClose,
  onCreated,
}: {
  onClose: () => void;
  onCreated: () => void;
}) {
  const [title, setTitle] = useState("");
  const [templateSource, setTemplateSource] =
    useState<"" | "system" | "user">("");
  const [templateRef, setTemplateRef] = useState("");
  const [templates, setTemplates] = useState<TemplateList>({
    system: [],
    user: [],
  });
  const [files, setFiles] = useState<FileList | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    apiGet<TemplateList>("/templates/list").then(setTemplates);
  }, []);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!title || !templateSource || !templateRef) return;

    try {
      setLoading(true);

      const program = await apiPost<{ id: number }>(
        "/funding-programs",
        {
          title,
          template_source: templateSource,
          template_ref: templateRef,
        }
      );

      /* ✅ Upload guideline PDFs (MULTI-FILE, CORRECT) */
      if (files && files.length > 0) {
        await apiUploadFiles(
          `/funding-programs/${program.id}/guidelines/upload`,
          Array.from(files)
        );
      }

      onCreated();
    } catch (e) {
      console.error(e);
      alert("Failed to create funding program");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className={styles.dialogOverlay} onClick={onClose}>
      <div
        className={styles.dialogBox}
        onClick={(e) => e.stopPropagation()}
      >
        <h3 className={styles.dialogTitle}>
          New Funding Program
        </h3>

        <form onSubmit={handleSubmit}>
          <label className={styles.formLabel}>
            Title *
          </label>
          <input
            className={styles.formInput}
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
          />

          <label className={styles.formLabel}>
            Template *
          </label>
          <select
            className={styles.formInput}
            value={templateSource}
            onChange={(e) => {
              setTemplateSource(
                e.target.value as "system" | "user"
              );
              setTemplateRef("");
            }}
          >
            <option value="">Select source</option>
            <option value="system">System</option>
            <option value="user">User</option>
          </select>

          {templateSource && (
            <select
              className={styles.formInput}
              value={templateRef}
              onChange={(e) =>
                setTemplateRef(e.target.value)
              }
              required
            >
              <option value="">Select template</option>
              {(templateSource === "system"
                ? templates.system
                : templates.user
              ).map((t) => (
                <option key={t.id} value={t.id}>
                  {t.name}
                </option>
              ))}
            </select>
          )}

          <label className={styles.formLabel}>
            Guidelines (PDF)
          </label>
          <input
            type="file"
            multiple
            accept="application/pdf"
            onChange={(e) =>
              setFiles(e.target.files)
            }
            className={styles.formFile}
          />

          <div className={styles.dialogActions}>
            <button
              type="button"
              className={styles.cancelButton}
              onClick={onClose}
            >
              Cancel
            </button>
            <button
              type="submit"
              className={styles.createButton}
              disabled={loading}
            >
              {loading ? "Creating…" : "Create"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
