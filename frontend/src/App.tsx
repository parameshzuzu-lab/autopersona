import { useCallback, useEffect, useState } from 'react';
import { Navigate, Route, Routes, useNavigate } from 'react-router-dom';
import { Sidebar } from './components/common/Sidebar';
import { Header } from './components/common/Header';
import { DashboardPage } from './pages/DashboardPage';
import { FeedPage } from './pages/FeedPage';
import { MemoryPage } from './pages/MemoryPage';
import { RejectedTopicsPage } from './pages/RejectedTopicsPage';
import { ActivityMonitorPage } from './pages/ActivityMonitorPage';
import { apiService } from './services/api';
import { MemoryOverview, Persona, PublishedPost, SchedulerStatus } from './types';

export function App() {
  const navigate = useNavigate();
  const [posts, setPosts] = useState<PublishedPost[]>([]);
  const [memory, setMemory] = useState<MemoryOverview>();
  const [persona, setPersona] = useState<Persona>();
  const [scheduler, setScheduler] = useState<SchedulerStatus>();
  const [isPublishing, setIsPublishing] = useState(false);

  const refreshOverview = useCallback(async () => {
    const [feed, memoryData, personaData] = await Promise.all([
      apiService.getFeed(), apiService.getMemory(), apiService.getPersona(),
    ]);
    setPosts(feed);
    setMemory(memoryData);
    setPersona(personaData.persona);
    setScheduler(personaData.scheduler);
  }, []);

  useEffect(() => { void refreshOverview(); }, [refreshOverview]);

  const triggerPublish = async () => {
    setIsPublishing(true);
    try {
      await apiService.triggerFeed();
      window.setTimeout(() => { void refreshOverview(); }, 1200);
    } finally {
      setIsPublishing(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#080c14] lg:flex">
      <Sidebar onTriggerPublish={triggerPublish} isPublishing={isPublishing} />
      <main className="min-w-0 flex-1">
        <Header persona={persona} scheduler={scheduler} />
        <div className="mx-auto max-w-7xl px-5 py-8 sm:px-8">
          <Routes>
            <Route path="/" element={<DashboardPage posts={posts} memory={memory} scheduler={scheduler} onNavigateToFeed={() => navigate('/feed')} />} />
            <Route path="/feed" element={<FeedPage posts={posts} />} />
            <Route path="/memory" element={<MemoryPage memory={memory} />} />
            <Route path="/rejected" element={<RejectedTopicsPage />} />
            <Route path="/activity" element={<ActivityMonitorPage />} />
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </div>
      </main>
    </div>
  );
}
