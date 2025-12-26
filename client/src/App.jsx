import UploadArea from "./components/UploadArea";
import JobCard from "./components/JobCard";
import SearchBar from "./components/SearchBar";
import SearchResults from "./components/SearchResults";
import ChatPanel from "./components/ChatPanel";

import { useJobs } from "./state/useJobs";
import { useSearch } from "./state/useSearch";
import { useChat } from "./state/useChat";

export default function App() {
  /* -------------------- Jobs (OCR lifecycle) -------------------- */
  const { jobs, addJob } = useJobs();

  /* -------------------- Search -------------------- */
  const { results, searching, handleSearch } = useSearch();

  /* -------------------- Chat (Document QA) -------------------- */
  const {
    selectedDoc,
    chatMessages,
    chatInput,
    chatLoading,
    setChatInput,
    openChatForDoc,
    closeChat,
    sendQuestion,
  } = useChat();

  return (
    <div className="container">
      {/* -------------------- Header -------------------- */}
      <header>
        <h1>Smart OCR & Tagging</h1>
        <p>
          Upload documents, search them, download results, and chat with content.
        </p>
      </header>

      {/* -------------------- Upload -------------------- */}
      <UploadArea onNewJob={addJob} />

      {/* -------------------- Search -------------------- */}
      <SearchBar onSearch={handleSearch} />

      <SearchResults
        items={results}
        searching={searching}
        onSelect={openChatForDoc}
      />

      {/* -------------------- OCR Jobs -------------------- */}
      <section className="jobs">
        {jobs.map((job) => (
          <JobCard key={job.id} job={job} />
        ))}
      </section>

      {/* -------------------- Chat Panel -------------------- */}
      {selectedDoc && (
        <ChatPanel
          selectedDoc={selectedDoc}
          chatMessages={chatMessages}
          chatInput={chatInput}
          chatLoading={chatLoading}
          setChatInput={setChatInput}
          handleSendQuestion={sendQuestion}
          onClose={closeChat}
        />
      )}
    </div>
  );
}
