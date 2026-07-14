import React, { useEffect, useState } from 'react';
import { usePlannerStore } from '../store/plannerStore';
import { api } from '../store/plannerStore';
import ReactMarkdown from 'react-markdown';
import { 
  Notebook, 
  Layers, 
  ScanLine, 
  FileText, 
  Upload, 
  Send,
  Loader2,
  CheckCircle,
  FileDown,
  Printer,
  ChevronRight,
  BookOpen
} from 'lucide-react';

export default function Notes() {
  const { exam, fetchDashboard } = usePlannerStore();
  const [topics, setTopics] = useState([]);
  const [selectedTopic, setSelectedTopic] = useState(null);
  const [activeTab, setActiveTab] = useState('notes'); // notes, flashcards, ocr, pdf_rag
  
  // Note details state
  const [noteContent, setNoteContent] = useState('');
  const [flashcards, setFlashcards] = useState([]);
  const [flippedCardId, setFlippedCardId] = useState(null);
  const [cardLoading, setCardLoading] = useState(false);
  const [noteLoading, setNoteLoading] = useState(false);

  // OCR state
  const [ocrFile, setOcrFile] = useState(null);
  const [ocrLoading, setOcrLoading] = useState(false);
  const [ocrResult, setOcrResult] = useState(null);

  // RAG state
  const [ragFile, setRagFile] = useState(null);
  const [ragLoading, setRagLoading] = useState(false);
  const [ragQuery, setRagQuery] = useState('');
  const [ragAnswer, setRagAnswer] = useState('');
  const [ragSources, setRagSources] = useState([]);
  const [ragSubmitLoading, setRagSubmitLoading] = useState(false);

  // Load topics
  useEffect(() => {
    if (exam) {
      axiosLoadTopics();
    }
  }, [exam]);

  const axiosLoadTopics = async () => {
    try {
      const res = await api.get(`/exams/${exam.id}/details`);
      setTopics(res.data.topics || []);
      if (res.data.topics?.length > 0 && !selectedTopic) {
        setSelectedTopic(res.data.topics[0]);
      }
    } catch (err) {
      console.error('Failed to load exam details topics', err);
    }
  };

  // Load Note & Flashcard on topic change
  useEffect(() => {
    if (selectedTopic) {
      loadTopicNote();
      loadTopicFlashcards();
    }
  }, [selectedTopic]);

  const loadTopicNote = async () => {
    setNoteLoading(true);
    try {
      const res = await api.get(`/progress/topics/${selectedTopic.id}/notes`);
      setNoteContent(res.data.content);
    } catch (err) {
      setNoteContent('Failed to load notes for this topic.');
    } finally {
      setNoteLoading(false);
    }
  };

  const loadTopicFlashcards = async () => {
    setCardLoading(true);
    try {
      const res = await api.get(`/progress/topics/${selectedTopic.id}/flashcards`);
      setFlashcards(res.data || []);
      setFlippedCardId(null);
    } catch (err) {
      setFlashcards([]);
    } finally {
      setCardLoading(false);
    }
  };

  // SM-2 Review Submission
  const handleReviewQuality = async (cardId, quality) => {
    try {
      await api.post('/progress/flashcards/review', {
        flashcard_id: cardId,
        quality: quality
      });
      alert(`Spaced interval rescheduled (Quality rating logged: ${quality}/5).`);
      // Reload flashcards to see rescheduled review dates if needed
      loadTopicFlashcards();
    } catch (err) {
      console.error('Failed to submit card quality score', err);
    }
  };

  // OCR Upload triggers
  const handleOcrSubmit = async (e) => {
    e.preventDefault();
    if (!ocrFile || !selectedTopic) {
      alert('Please select an image file first.');
      return;
    }
    setOcrLoading(true);
    setOcrResult(null);
    
    const formData = new FormData();
    formData.append('file', ocrFile);
    formData.append('topic_id', selectedTopic.id);
    
    try {
      const res = await api.post('/ai/ocr-upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setOcrResult(res.data);
      // Refresh note
      loadTopicNote();
    } catch (err) {
      alert('OCR Process failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setOcrLoading(false);
    }
  };

  // RAG PDF Upload triggers
  const handleRagUpload = async (e) => {
    e.preventDefault();
    if (!ragFile) {
      alert('Please select a PDF document first.');
      return;
    }
    setRagLoading(true);
    
    const formData = new FormData();
    formData.append('file', ragFile);
    
    try {
      await api.post('/ai/pdf-upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      alert('PDF indexed successfully. Chunks generated and embedded in search.');
      setRagFile(null);
    } catch (err) {
      alert('PDF Indexing failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      setRagLoading(false);
    }
  };

  const handleRagQuerySubmit = async (e) => {
    e.preventDefault();
    if (!ragQuery) return;
    setRagSubmitLoading(true);
    setRagAnswer('');
    
    try {
      const res = await api.post('/ai/pdf-query', { query: ragQuery });
      setRagAnswer(res.data.answer);
      setRagSources(res.data.sources || []);
    } catch (err) {
      setRagAnswer('Failed to query RAG models: ' + (err.response?.data?.detail || err.message));
    } finally {
      setRagSubmitLoading(false);
    }
  };

  return (
    <div className="space-y-8 max-w-6xl mx-auto pb-16">
      {/* Top Banner */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Learning Desk</h1>
          <p className="text-dark-300 text-sm mt-1">Review summaries, practice spaced recall cards, and search document resources.</p>
        </div>
      </div>

      {!exam ? (
        <div className="glass-card text-center py-16 px-6 max-w-xl mx-auto">
          <Notebook size={32} className="text-dark-400 mx-auto mb-4" />
          <h3 className="text-lg font-bold text-white mb-2">No Active Study Desk</h3>
          <p className="text-dark-300 text-sm">Please configure an active exam schedule on the dashboard first.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Side Topic selection bar */}
          <div className="lg:col-span-1 glass-card p-4">
            <h3 className="font-bold text-xs text-dark-300 uppercase tracking-widest mb-4">Syllabus Chapters</h3>
            <div className="flex flex-col gap-2 max-h-[60vh] overflow-y-auto pr-1">
              {topics.map((t) => {
                const isSelected = selectedTopic?.id === t.id;
                return (
                  <button
                    key={t.id}
                    onClick={() => setSelectedTopic(t)}
                    className={`w-full text-left p-3 rounded-xl border transition-all duration-150 flex items-center justify-between cursor-pointer ${
                      isSelected 
                        ? 'bg-blue-600/10 border-blue-500 text-blue-300' 
                        : 'bg-dark-950/40 border-dark-800/80 hover:bg-dark-900/60 hover:border-dark-700 text-dark-200'
                    }`}
                  >
                    <div className="truncate pr-2">
                      <div className="text-xs font-semibold truncate">{t.title}</div>
                      <span className="text-[10px] text-dark-400 font-medium block truncate">{t.subject_name}</span>
                    </div>
                    <ChevronRight size={14} className={isSelected ? 'text-blue-400' : 'text-dark-500'} />
                  </button>
                );
              })}
            </div>
          </div>

          {/* Central Workspace area */}
          <div className="lg:col-span-3 space-y-6">
            {/* Header selection tab */}
            <div className="flex gap-2 p-1.5 bg-dark-950 border border-dark-800 rounded-2xl w-fit">
              <button
                onClick={() => setActiveTab('notes')}
                className={`flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl cursor-pointer ${
                  activeTab === 'notes' ? 'bg-dark-900 text-white' : 'text-dark-300 hover:text-dark-50'
                }`}
              >
                <Notebook size={14} /> AI Notes
              </button>
              <button
                onClick={() => setActiveTab('flashcards')}
                className={`flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl cursor-pointer ${
                  activeTab === 'flashcards' ? 'bg-dark-900 text-white' : 'text-dark-300 hover:text-dark-50'
                }`}
              >
                <Layers size={14} /> Flashcards (SM-2)
              </button>
              <button
                onClick={() => setActiveTab('ocr')}
                className={`flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl cursor-pointer ${
                  activeTab === 'ocr' ? 'bg-dark-900 text-white' : 'text-dark-300 hover:text-dark-50'
                }`}
              >
                <ScanLine size={14} /> OCR Scan
              </button>
              <button
                onClick={() => setActiveTab('pdf_rag')}
                className={`flex items-center gap-2 px-4 py-2 text-xs font-semibold rounded-xl cursor-pointer ${
                  activeTab === 'pdf_rag' ? 'bg-dark-900 text-white' : 'text-dark-300 hover:text-dark-50'
                }`}
              >
                <FileText size={14} /> PDF Chat (RAG)
              </button>
            </div>

            {/* Note Workspace display */}
            <div className="glass-card p-6 min-h-[50vh]">
              {selectedTopic && (
                <div className="mb-6 flex justify-between items-center pb-4 border-b border-dark-800">
                  <div>
                    <h2 className="text-xl font-extrabold text-white">{selectedTopic.title}</h2>
                    <span className="text-xs text-dark-400">Notes generated on topic values</span>
                  </div>

                  {activeTab === 'notes' && (
                    <div className="flex gap-2">
                      <button 
                        onClick={() => window.print()}
                        className="p-2.5 bg-dark-950 hover:bg-dark-800 border border-dark-800 text-dark-300 rounded-xl hover:text-white transition-all cursor-pointer"
                        title="Print notes"
                      >
                        <Printer size={16} />
                      </button>
                    </div>
                  )}
                </div>
              )}

              {/* TABS CONTROLLERS */}
              {activeTab === 'notes' && (
                noteLoading ? (
                  <div className="py-20 flex justify-center items-center gap-2 text-dark-300 text-sm">
                    <Loader2 className="animate-spin text-blue-500" size={18} /> Loading study notes...
                  </div>
                ) : (
                  <article className="prose prose-invert max-w-none text-dark-200 text-sm leading-relaxed space-y-4">
                    <ReactMarkdown>{noteContent}</ReactMarkdown>
                  </article>
                )
              )}

              {activeTab === 'flashcards' && (
                cardLoading ? (
                  <div className="py-20 flex justify-center items-center gap-2 text-dark-300 text-sm">
                    <Loader2 className="animate-spin text-purple-500" size={18} /> Loading flashcards...
                  </div>
                ) : flashcards.length === 0 ? (
                  <div className="py-12 text-center text-dark-400 text-sm">
                    No flashcards generated for this topic yet. Generate the study plan to populate flashcards.
                  </div>
                ) : (
                  <div className="space-y-8">
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      {flashcards.map((card) => {
                        const isFlipped = flippedCardId === card.id;
                        return (
                          <div 
                            key={card.id}
                            className="glass-card min-h-[180px] p-6 flex flex-col justify-between cursor-pointer border border-dark-850 hover:border-dark-700 bg-dark-900/20"
                          >
                            <div onClick={() => setFlippedCardId(isFlipped ? null : card.id)} className="flex-1">
                              <span className="text-[9px] uppercase tracking-widest text-dark-400 font-bold">
                                {isFlipped ? 'Answer' : 'Question'}
                              </span>
                              <p className="text-dark-100 text-sm font-semibold mt-2 leading-relaxed">
                                {isFlipped ? card.answer : card.question}
                              </p>
                            </div>
                            
                            {isFlipped ? (
                              <div className="mt-4 pt-4 border-t border-dark-850 flex flex-col gap-2.5">
                                <span className="text-[9px] uppercase tracking-widest text-dark-400 font-bold">Grade Recall Quality (SM-2)</span>
                                <div className="flex gap-1.5 justify-between">
                                  {[1, 2, 3, 4, 5].map((val) => (
                                    <button
                                      key={val}
                                      onClick={(e) => {
                                        e.stopPropagation();
                                        handleReviewQuality(card.id, val);
                                      }}
                                      className={`flex-1 text-[10px] font-bold py-1.5 rounded transition-all active:scale-90 ${
                                        val >= 3 
                                          ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 hover:bg-emerald-500/20' 
                                          : 'bg-red-500/10 text-red-400 border border-red-500/20 hover:bg-red-500/20'
                                      }`}
                                    >
                                      {val}
                                    </button>
                                  ))}
                                </div>
                              </div>
                            ) : (
                              <span className="text-[10px] text-blue-400 font-bold self-end mt-4">Click card to reveal answer</span>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </div>
                )
              )}

              {activeTab === 'ocr' && (
                <div className="space-y-6 max-w-xl mx-auto py-4">
                  <div className="text-center p-6 border-2 border-dashed border-dark-800 rounded-3xl bg-dark-950/20">
                    <ScanLine size={32} className="text-dark-400 mx-auto mb-4" />
                    <h3 className="font-bold text-white text-sm mb-1">OCR Upload Tool</h3>
                    <p className="text-xs text-dark-400 max-w-xs mx-auto mb-6">Upload photos of handwritten pages or textbook sheets to convert them into markdown summaries & quizzes.</p>
                    
                    <input 
                      type="file" 
                      accept="image/*" 
                      onChange={(e) => setOcrFile(e.target.files?.[0] || null)}
                      className="hidden"
                      id="ocr-file-picker"
                    />
                    <label 
                      htmlFor="ocr-file-picker"
                      className="btn-secondary text-xs max-w-xs mx-auto cursor-pointer"
                    >
                      <Upload size={14} /> {ocrFile ? ocrFile.name : 'Select Study Image'}
                    </label>
                    
                    {ocrFile && (
                      <button 
                        onClick={handleOcrSubmit}
                        disabled={ocrLoading}
                        className="btn-primary text-xs font-bold w-full max-w-xs mx-auto mt-4 cursor-pointer"
                      >
                        {ocrLoading ? 'Scanning contents...' : 'Process Image OCR'}
                      </button>
                    )}
                  </div>

                  {ocrResult && (
                    <div className="space-y-6 pt-6 border-t border-dark-850">
                      <div className="p-4 bg-emerald-500/5 border border-emerald-500/20 text-emerald-300 rounded-xl text-xs font-semibold flex items-center gap-2">
                        <CheckCircle size={16} /> Successfully extracted content and added summary notes.
                      </div>
                      
                      <div className="space-y-3">
                        <h4 className="font-bold text-sm text-dark-100 uppercase tracking-widest">Extracted Core Text</h4>
                        <div className="p-4 bg-dark-950/40 rounded-xl border border-dark-850 text-xs text-dark-300 font-mono leading-relaxed whitespace-pre-wrap">
                          {ocrResult.extracted_text}
                        </div>
                      </div>

                      <div className="space-y-3">
                        <h4 className="font-bold text-sm text-dark-100 uppercase tracking-widest">Generated Quick Quiz</h4>
                        <div className="space-y-3">
                          {ocrResult.quiz.map((q, idx) => (
                            <div key={idx} className="p-4 bg-dark-950/20 rounded-xl border border-dark-850 text-xs">
                              <p className="font-bold text-dark-100">{idx+1}. {q.question_text}</p>
                              <div className="grid grid-cols-2 gap-2 mt-2">
                                {q.options.map((opt, oIdx) => (
                                  <div key={oIdx} className="bg-dark-950 px-3 py-1.5 rounded border border-dark-850 text-dark-300">
                                    {opt}
                                  </div>
                                ))}
                              </div>
                              <p className="mt-2 text-emerald-400 font-bold">Answer: {q.correct_answer}</p>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              )}

              {activeTab === 'pdf_rag' && (
                <div className="space-y-8">
                  {/* PDF Upload Section */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-center bg-dark-950/40 border border-dark-850 p-6 rounded-2xl">
                    <div className="md:col-span-2">
                      <h4 className="font-bold text-sm text-white mb-1">RAG Document Indexer</h4>
                      <p className="text-xs text-dark-400">Upload course PDFs, slide decks, or papers. The system automatically chunks the pages to answer RAG-based search queries.</p>
                    </div>
                    <div>
                      <input 
                        type="file" 
                        accept="application/pdf"
                        onChange={(e) => setRagFile(e.target.files?.[0] || null)}
                        className="hidden"
                        id="rag-file-picker"
                      />
                      <label 
                        htmlFor="rag-file-picker"
                        className="btn-secondary text-xs w-full cursor-pointer"
                      >
                        <Upload size={14} /> {ragFile ? ragFile.name : 'Select PDF Paper'}
                      </label>
                      {ragFile && (
                        <button
                          onClick={handleRagUpload}
                          disabled={ragLoading}
                          className="btn-primary text-xs font-bold w-full mt-3 cursor-pointer"
                        >
                          {ragLoading ? 'Indexing chunks...' : 'Embed PDF Chunks'}
                        </button>
                      )}
                    </div>
                  </div>

                  {/* RAG Query Panel */}
                  <div className="space-y-4">
                    <form onSubmit={handleRagQuerySubmit} className="flex gap-3">
                      <input 
                        type="text" 
                        placeholder="Search your notes or ask questions (e.g. explain TCP congestion control rules)"
                        value={ragQuery}
                        onChange={(e) => setRagQuery(e.target.value)}
                        className="flex-1 glass-input py-3"
                      />
                      <button 
                        type="submit"
                        disabled={ragSubmitLoading}
                        className="btn-primary py-3.5 px-6 font-bold cursor-pointer"
                      >
                        {ragSubmitLoading ? <Loader2 className="animate-spin" size={18} /> : <Send size={18} />}
                      </button>
                    </form>

                    {ragAnswer && (
                      <div className="glass-card p-6 bg-dark-950/60 border border-dark-850">
                        <div className="flex items-center gap-2 mb-4 text-xs font-bold text-indigo-400 uppercase tracking-widest">
                          <BookOpen size={16} />
                          <span>RAG Document Tutor Response</span>
                        </div>
                        <article className="prose prose-invert max-w-none text-xs text-dark-200 leading-relaxed whitespace-pre-wrap">
                          {ragAnswer}
                        </article>
                        
                        {ragSources.length > 0 && (
                          <div className="mt-4 pt-4 border-t border-dark-850 flex gap-2 items-center flex-wrap">
                            <span className="text-[10px] text-dark-400 font-bold">Context Sources:</span>
                            {ragSources.map((src, idx) => (
                              <span key={idx} className="text-[9px] bg-dark-950 text-dark-300 border border-dark-800 px-2 py-0.5 rounded font-mono">
                                {src}
                              </span>
                            ))}
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
