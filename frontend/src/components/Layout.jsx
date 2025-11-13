  import { useState } from 'react';
import { Menu } from 'lucide-react';
import Sidebar from './Sidebar';
import Dashboard from './Dashboard';
import Simulation from '../pages/Simulation';

export default function Layout() {
  const [currentView, setCurrentView] = useState('dashboard');
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const toggleSidebar = () => {
    setSidebarOpen(!sidebarOpen);
  };

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50 dark:bg-gray-900">
      <Sidebar
        currentView={currentView}
        onViewChange={setCurrentView}
        isOpen={sidebarOpen}
        onToggle={toggleSidebar}
      />
      
      <main
        className={`flex-1 overflow-y-auto transition-all duration-300 ${
          sidebarOpen ? 'ml-64' : 'ml-0'
        }`}
      >
        {/* Botón para abrir sidebar cuando está cerrado */}
        {!sidebarOpen && (
          <button
            onClick={toggleSidebar}
            className="fixed top-4 left-4 z-50 p-2 bg-blue-600 text-white rounded-lg shadow-lg hover:bg-blue-700 transition-colors"
            aria-label="Abrir sidebar"
          >
            <Menu className="w-6 h-6" />
          </button>
        )}
        
        {currentView === 'dashboard' && <Dashboard />}
        {currentView === 'simulation' && <Simulation />}
      </main>
    </div>
  );
}

