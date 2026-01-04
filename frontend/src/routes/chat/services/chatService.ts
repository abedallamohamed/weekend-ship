import { httpService } from "$lib/services/httpService";
import type { SendMessageRequest, ConversationData } from "../types/chat";

export const chatService = {
  sendMessage: (data: SendMessageRequest, customHeaders?: Record<string, string>) => {
    return httpService.post<ConversationData>('/api/conversations', data, customHeaders);
  },

  getConversations: (customHeaders?: Record<string, string>) => {
    return httpService.get<ConversationData[]>('/api/conversations', customHeaders);
  },

  clearConversations: async (): Promise<void> => {
    return httpService.delete<void>('/api/conversations');
  },

  updateTaskStatus: (
    conversationId: string,
    timeBlockIndex: number,
    taskIndex: number,
    completed: boolean,
    customHeaders?: Record<string, string>
  ) => {
    return httpService.patch<{ message: string }>(
      `/api/conversations/${conversationId}/tasks`,
      {
        time_block_index: timeBlockIndex,
        task_index: taskIndex,
        completed
      },
      customHeaders
    );
  },
};
