import { useCallback, useRef, useState } from "react";
import { LuCloudUpload } from "react-icons/lu";

export default function FileUploader({ onAnalyze, loading }) {
  const [file, setFile] = useState(null);
  const [question, setQuestion] = useState("");
  const dropRef = useRef(null);

  const handleFiles = useCallback((files) => {
    if (files && files.length) {
      setFile(files[0]);
    }
  }, []);

  const handleDrop = useCallback(
    (event) => {
      event.preventDefault();
      handleFiles(event.dataTransfer.files);
      dropRef.current.classList.remove("uploader-drop-active");
    },
    [handleFiles],
  );

  const handleDragOver = useCallback((event) => {
    event.preventDefault();
    dropRef.current.classList.add("uploader-drop-active");
  }, []);

  const handleDragLeave = useCallback((event) => {
    event.preventDefault();
    dropRef.current.classList.remove("uploader-drop-active");
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file || !question) return;
    await onAnalyze({ file, question });
    setQuestion("");
  };

  return (
    <div className="uploader-container">
      <form className="uploader-form" onSubmit={handleSubmit}>
        <div
          ref={dropRef}
          className="uploader-dropzone"
          onDrop={handleDrop}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
        >
          <LuCloudUpload size={32} />
          <p className="uploader-title">
            Drag & drop a document or
            <label className="uploader-file-label">
              <input
                type="file"
                accept=".pdf,.docx,.txt"
                onChange={(event) => handleFiles(event.target.files)}
                hidden
              />
              <span>browse</span>
            </label>
          </p>
          <p className="uploader-hint">Supported: PDF, DOCX, TXT (reports, research, market studies) up to 20MB</p>
          {file && (
            <div className="uploader-file-chip">
              <span>{file.name}</span>
              <small>{(file.size / (1024 * 1024)).toFixed(2)} MB</small>
            </div>
          )}
        </div>

        <div className="uploader-question">
          <label htmlFor="primary-question">Primary question for the AI</label>
          <div className="uploader-input-row">
            <input
              id="primary-question"
              type="text"
              placeholder="What are the key insights? What opportunities exist? What trends should I know?"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
            />
            <button type="submit" disabled={!file || !question || loading}>
              {loading ? "Analyzing..." : "Analyze"}
            </button>
          </div>
        </div>
      </form>
    </div>
  );
}

