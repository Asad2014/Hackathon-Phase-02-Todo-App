'use client';

import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Plus, Calendar, ListChecks } from 'lucide-react';

import { Button } from '@/components/ui/button';
import { TaskList } from '@/components/dashboard/task-list';
import { EmptyState } from '@/components/dashboard/empty-state';
import { Task } from '@/types';
import { tasksApi } from '@/lib/api-client';
import { CreateTaskModal } from '@/components/dashboard/create-task-modal';
import { useSession } from '@/lib/auth';
import { ProfileDropdown } from '@/components/dashboard/profile-dropdown';

import { useRouter } from 'next/navigation';

export default function DashboardPage() {
  const router = useRouter();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const { data: sessionData, isPending: sessionLoading } = useSession();

  useEffect(() => {
    // Wait for session check to complete
    if (sessionLoading) return;

    // Redirect if no session
    if (!sessionData) {
      router.push('/login');
      return;
    }

    const fetchTasks = async () => {
      try {
        if (sessionData?.user?.id) {
          const data = await tasksApi.getAll(sessionData.user.id);
          setTasks(data);
        }
      } catch (error) {
        console.error('Failed to fetch tasks:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTasks();
  }, [sessionData, sessionLoading, router]);

  const handleTaskCreated = (newTask: Task) => {
    setTasks(prev => {
      // Filter out any existing tasks with the same ID to prevent duplicates
      const filteredTasks = prev.filter(task => task.id !== newTask.id);
      // Add the new task to the beginning of the array
      return [newTask, ...filteredTasks];
    });
    setShowCreateModal(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <div className="absolute inset-0 bg-gradient-to-br from-blue-600/5 via-indigo-600/5 to-purple-600/5 dark:from-blue-900/30 dark:via-indigo-900/30 dark:to-purple-900/30"></div>
        <div className="relative container mx-auto p-6">
          <div className="space-y-6">
            {[...Array(3)].map((_, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.1 }}
                className="p-6 border rounded-xl bg-white/80 backdrop-blur-sm shadow-lg dark:bg-gray-800/80"
              >
                <div className="h-4 bg-gradient-to-r from-blue-200 to-purple-200 rounded w-3/4 mb-3 dark:from-blue-700 dark:to-purple-700"></div>
                <div className="h-3 bg-gradient-to-r from-blue-100 to-purple-100 rounded w-1/2 dark:from-blue-600 dark:to-purple-600"></div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <div className="absolute inset-0 bg-gradient-to-br from-blue-600/5 via-indigo-600/5 to-purple-600/5 dark:from-blue-900/30 dark:via-indigo-900/30 dark:to-purple-900/30"></div>
      <div className="relative container mx-auto p-6">
        <div className="mb-8">
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 p-8 rounded-2xl shadow-xl">
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
              <div className="text-white">
                <h1 className="text-4xl font-bold tracking-tight">Dashboard</h1>
                <p className="text-blue-100 mt-2 text-lg">
                  Welcome back! Here's what you need to focus on today.
                </p>
              </div>
              <div className="flex items-center gap-3">
                <Button
                  onClick={() => setShowCreateModal(true)}
                  className="bg-white text-blue-600 hover:bg-blue-50 h-12 px-6 rounded-xl font-semibold shadow-lg hover:shadow-xl transition-all duration-200"
                >
                  <Plus className="mr-2 h-5 w-5" />
                  Add Task
                </Button>

                {sessionData?.user && (
                  <div className="bg-white/20 p-1.5 rounded-full backdrop-blur-md shadow-lg border border-white/10">
                    <ProfileDropdown
                      user={{
                        name: sessionData.user.name || sessionData.user.email || 'User',
                        email: sessionData.user.email
                      }}
                    />
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {tasks.length > 0 ? (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.3 }}
          >
            <div className="bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg p-6 dark:bg-gray-800/80">
              <TaskList tasks={tasks} setTasks={setTasks} />
            </div>
          </motion.div>
        ) : (
          <div className="flex justify-center items-center min-h-[400px]">
            <EmptyState
              icon={ListChecks}
              title="No tasks yet"
              description="Get started by creating a new task."
              buttonText="Create Task"
              onButtonClick={() => setShowCreateModal(true)}
            />
          </div>
        )}

        <CreateTaskModal
          isOpen={showCreateModal}
          onClose={() => setShowCreateModal(false)}
          onTaskCreated={handleTaskCreated}
        />
      </div>
    </div>
  );
}