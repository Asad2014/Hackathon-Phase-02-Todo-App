import { toast } from 'sonner';

// Export toast directly
export { toast };

// For compatibility with shadcn/ui pattern
export function useToast() {
  return {
    toast: (props: { title?: string; description?: string; variant?: 'destructive' | 'default' }) => {
      if (props.variant === 'destructive') {
        toast.error(props.title, {
          description: props.description
        });
      } else {
        toast.success(props.title, {
          description: props.description
        });
      }
    },
  };
}