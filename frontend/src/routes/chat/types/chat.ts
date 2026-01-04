export interface Task {
  task: string;
  essential: boolean;
  estimatedTime: string;
  completed: boolean;
}

export interface TimeBlock {
  timeBlock: string;
  tasks: Task[];
}

export interface ProjectPlan {
  projectOverview: string;
  techStack: string[];
  timeline: TimeBlock[];
  tips: string[];
}

export interface SendMessageRequest {
  message: string;
  mode?: 'basic' | 'detailed';
}

export interface ConversationData {
  id: string;
  userMessage: string;
  botResponse: string;
  projectPlan?: ProjectPlan;
  timestamp: string;
}
