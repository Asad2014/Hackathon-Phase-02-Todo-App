import { Task } from '@/types';
import { TaskItem } from '@/components/dashboard/task-item';

interface TaskListProps {
  tasks: Task[];
  setTasks: React.Dispatch<React.SetStateAction<Task[]>>;
}

export function TaskList({ tasks, setTasks }: TaskListProps) {
  // Remove any duplicate tasks by ID to ensure unique keys
  const uniqueTasks = tasks.reduce<Task[]>((acc, task) => {
    if (!acc.some(t => t.id === task.id)) {
      acc.push(task);
    }
    return acc;
  }, []);

  return (
    <div className="space-y-2">
      {uniqueTasks.map((task) => (
        <TaskItem
          key={task.id}
          task={task}
          onUpdate={(updatedTask) => {
            setTasks(prev => {
              // Filter out any existing tasks with the same ID to prevent duplicates
              const filteredTasks = prev.filter(t => t.id !== updatedTask.id);
              // Replace with updated task
              return [...filteredTasks, updatedTask];
            });
          }}
          onDelete={(deletedTaskId) => {
            setTasks(prev => prev.filter(t => t.id.toString() !== deletedTaskId));
          }}
        />
      ))}
    </div>
  );
}