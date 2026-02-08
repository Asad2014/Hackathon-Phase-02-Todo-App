import { Button } from '@/components/ui/button';

interface EmptyStateProps {
  icon: React.ElementType;
  title: string;
  description: string;
  buttonText?: string;
  onButtonClick?: () => void;
}

export function EmptyState({
  icon: Icon,
  title,
  description,
  buttonText,
  onButtonClick
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="mb-4 rounded-full bg-muted p-3">
        <Icon className="h-8 w-8 text-muted-foreground" />
      </div>
      <h3 className="mb-1 text-xl font-semibold">{title}</h3>
      <p className="mb-4 text-sm text-muted-foreground">{description}</p>
      {buttonText && (
        <Button onClick={onButtonClick}>
          {buttonText}
        </Button>
      )}
    </div>
  );
}