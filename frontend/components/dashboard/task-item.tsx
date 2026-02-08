'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Checkbox } from '@/components/ui/checkbox';
import { Button } from '@/components/ui/button';
import { Trash2, Edit3 } from 'lucide-react';

import { Task } from '@/types';
import { tasksApi } from '@/lib/api-client';
import { useSession } from '@/lib/auth';

interface TaskItemProps {
  task: Task;
  onUpdate: (updatedTask: Task) => void;
  onDelete: (taskId: string) => void;
}

export function TaskItem({ task, onUpdate, onDelete }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editText, setEditText] = useState(task.title);
  const [isLoading, setIsLoading] = useState(false);
  const { data: sessionData } = useSession();

  const handleToggleComplete = async () => {
    if (!sessionData?.user?.id) {
      console.error('User not authenticated');
      return;
    }

    setIsLoading(true);
    try {
      const updatedTask = await tasksApi.update(sessionData.user.id, task.id.toString(), {
        ...task,
        completed: !task.completed
      });

      onUpdate(updatedTask);
    } catch (error) {
      console.error('Failed to update task:', error);
      // Handle message channel errors gracefully
      if (error instanceof Error && error.message.includes('message channel closed')) {
        // Update locally if API fails due to message channel issues
        onUpdate({...task, completed: !task.completed});
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveEdit = async () => {
    if (!sessionData?.user?.id) {
      console.error('User not authenticated');
      return;
    }

    setIsLoading(true);
    try {
      const updatedTask = await tasksApi.update(sessionData.user.id, task.id.toString(), {
        ...task,
        title: editText
      });

      onUpdate(updatedTask);
      setIsEditing(false);
    } catch (error) {
      console.error('Failed to update task:', error);
      // Handle message channel errors gracefully
      if (error instanceof Error && error.message.includes('message channel closed')) {
        // Update locally if API fails due to message channel issues
        onUpdate({...task, title: editText});
        setIsEditing(false);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async () => {
    if (!sessionData?.user?.id) {
      console.error('User not authenticated');
      return;
    }

    setIsLoading(true);
    try {
      await tasksApi.delete(sessionData.user.id, task.id.toString());
      onDelete(task.id.toString());
    } catch (error) {
      console.error('Failed to delete task:', error);
      // Handle message channel errors gracefully
      if (error instanceof Error && error.message.includes('message channel closed')) {
        // Delete locally if API fails due to message channel issues
        onDelete(task.id.toString());
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -20 }}
      className={`p-4 border rounded-lg flex items-start gap-3 ${
        task.completed ? 'bg-green-50/30 dark:bg-green-950/20' : 'bg-background'
      }`}
    >
      <Checkbox
        checked={task.completed}
        onCheckedChange={handleToggleComplete}
        disabled={isLoading}
        className="mt-0.5"
      />

      <div className="flex-1 min-w-0">
        {isEditing ? (
          <input
            type="text"
            value={editText}
            onChange={(e) => setEditText(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSaveEdit()}
            className="w-full bg-transparent border-b border-gray-300 dark:border-gray-600 focus:outline-none focus:border-blue-500"
            autoFocus
          />
        ) : (
          <div>
            <p className={`${task.completed ? 'line-through text-muted-foreground' : ''}`}>
              {task.title}
            </p>
            {task.description && (
              <p className="text-sm text-muted-foreground mt-1">{task.description}</p>
            )}
          </div>
        )}
      </div>

      <div className="flex gap-1">
        {!isEditing && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setIsEditing(true)}
            disabled={isLoading}
          >
            <Edit3 className="h-4 w-4" />
          </Button>
        )}

        {isEditing ? (
          <Button
            variant="outline"
            size="sm"
            onClick={handleSaveEdit}
            disabled={isLoading}
          >
            Save
          </Button>
        ) : null}

        <Button
          variant="ghost"
          size="sm"
          onClick={handleDelete}
          disabled={isLoading}
        >
          <Trash2 className="h-4 w-4" />
        </Button>
      </div>
    </motion.div>
  );
}