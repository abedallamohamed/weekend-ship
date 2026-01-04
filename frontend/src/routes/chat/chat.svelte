<script lang="ts">
	import { onMount, tick } from 'svelte';
	import { marked } from 'marked';
	import { chatService } from './services/chatService';
	import { Sidebar } from '$lib/sidebar';
	import type { ConversationData, ProjectPlan } from './types/chat';

	interface ChatMessage {
		role: 'user' | 'assistant';
		content: string;
		projectPlan?: ProjectPlan;
		conversationId?: string;  // Track which conversation this message belongs to
		status?: 'pending' | 'sent' | 'error'; // Message status for user messages
	}

	let messages: ChatMessage[] = [];
	let inputValue = '';
	let isLoading = true;
	let isSending = false;
	let messagesContainer: HTMLElement;
	let planningMode: 'basic' | 'detailed' = 'basic'; // Mode selector
	let sidebarOpen = true;

	// Configure marked for proper rendering
	marked.setOptions({
		breaks: true, // Respect \n line breaks
		gfm: true // GitHub Flavored Markdown
	});

	function renderMarkdown(content: string): string {
		return marked.parse(content) as string;
	}

	async function scrollToBottom(smooth = false) {
		await tick();
		if (messagesContainer) {
			messagesContainer.scrollTo({
				top: messagesContainer.scrollHeight,
				behavior: smooth ? 'smooth' : 'auto'
			});
		}
	}

	async function scrollToUserMessage() {
		await tick();
		if (messagesContainer && messages.length >= 2) {
			// Find the most recent user message element (second to last message)
			const userMessages = messagesContainer.querySelectorAll('.message-wrapper.user');
			const lastUserMessage = userMessages[userMessages.length - 1];
			
			if (lastUserMessage) {
				// Scroll so that the user message is at the top of viewport
				const containerRect = messagesContainer.getBoundingClientRect();
				const messageRect = lastUserMessage.getBoundingClientRect();
				const scrollTop = messagesContainer.scrollTop + (messageRect.top - containerRect.top);
				
				messagesContainer.scrollTo({
					top: scrollTop,
					behavior: 'smooth'
				});
			}
		}
	}

	onMount(async () => {
		try {
			const conversations = await chatService.getConversations();
			messages = conversations.flatMap((conv: ConversationData) => [
				{ role: 'user' as const, content: conv.userMessage },
				{ 
					role: 'assistant' as const, 
					content: conv.botResponse, 
					projectPlan: conv.projectPlan,
					conversationId: conv.id
				}
			]);
			// Scroll instantly to bottom after loading
			await scrollToBottom(false);
		} catch (error) {
			console.error('Error loading conversations:', error);
		} finally {
			isLoading = false;
		}
	});

	async function sendMessage() {
		if (!inputValue.trim() || isSending) return;

		const userMessage = inputValue.trim();
		inputValue = '';
		isSending = true;

		// Add user message immediately with pending status
		const userMessageObj = { role: 'user' as const, content: userMessage, status: 'pending' as const };
		messages = [...messages, userMessageObj];
		// Smooth scroll after adding user message
		await scrollToBottom(true);

		try {
			const response = await chatService.sendMessage({ 
				message: userMessage, 
				mode: planningMode 
			});
			
			// Update user message status to 'sent'
			messages = messages.map((msg, index) => 
				index === messages.length - 1 && msg.role === 'user' 
					? { ...msg, status: 'sent' as const }
					: msg
			);
			
			// Add bot response with projectPlan and conversationId
			messages = [...messages, { 
				role: 'assistant', 
				content: response.botResponse,
				projectPlan: response.projectPlan,
				conversationId: response.id
			}];
		} catch (error) {
			console.error('Error sending message:', error);
			
			// Update user message status to 'error'
			messages = messages.map((msg, index) => 
				index === messages.length - 1 && msg.role === 'user' 
					? { ...msg, status: 'error' as const }
					: msg
			);
			
			messages = [...messages, { role: 'assistant', content: 'Sorry, something went wrong. Please try again.' }];
		} finally {
			// Scroll to user message to see start of conversation
			await scrollToUserMessage();
			isSending = false;
		}
	}

	async function clearChat() {
		if (!confirm('Are you sure you want to clear the conversation and start fresh?')) return;

		try {
			await chatService.clearConversations();
			messages = [];
		} catch (error) {
			console.error('Error clearing conversations:', error);
			alert('Failed to clear conversations. Please try again.');
		}
	}

	function handleKeydown(event: KeyboardEvent) {
		if (event.key === 'Enter' && !event.shiftKey) {
			event.preventDefault();
			sendMessage();
		}
	}

	async function toggleTaskCompletion(
		conversationId: string,
		timeBlockIndex: number,
		taskIndex: number,
		currentStatus: boolean
	) {
		try {
			// Update locally first for instant feedback
			messages = messages.map(msg => {
				if (msg.conversationId === conversationId && msg.projectPlan) {
					const updatedPlan = { ...msg.projectPlan };
					updatedPlan.timeline[timeBlockIndex].tasks[taskIndex].completed = !currentStatus;
					return { ...msg, projectPlan: updatedPlan };
				}
				return msg;
			});

			// Then sync with backend
			await chatService.updateTaskStatus(
				conversationId,
				timeBlockIndex,
				taskIndex,
				!currentStatus
			);
		} catch (error) {
			console.error('Error updating task status:', error);
			// Revert on error
			messages = messages.map(msg => {
				if (msg.conversationId === conversationId && msg.projectPlan) {
					const updatedPlan = { ...msg.projectPlan };
					updatedPlan.timeline[timeBlockIndex].tasks[taskIndex].completed = currentStatus;
					return { ...msg, projectPlan: updatedPlan };
				}
				return msg;
			});
		}
	}
</script>

<div class="app-layout">
	<!-- Sidebar -->
	<Sidebar bind:isOpen={sidebarOpen} />

	<!-- Main content -->
	<main class="main-content">
		<div class="chat-container">
			<header class="chat-header">
				<h1>Plan your weekend project</h1>
				<p>Tell me what you want to build and I'll create a detailed plan</p>
			</header>

			<button class="new-chat-btn" on:click={clearChat} title="Start new conversation">
				<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
					<path d="M12 20h9"></path>
					<path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z"></path>
				</svg>
				New Chat
			</button>
	
	<div class="messages" bind:this={messagesContainer}>
		{#if isLoading}
			<div class="loading">Loading conversations...</div>
		{:else if messages.length === 0}
			<div class="empty">No conversations yet. Start chatting!</div>
		{:else}
			{#each messages as message}
				<div class="message-wrapper {message.role}" class:pending={message.status === 'pending'} class:error={message.status === 'error'}>
					<div class="message {message.role}">
						<div class="message-content">
							{@html renderMarkdown(message.content)}
						</div>
						
						{#if message.role === 'user' && message.status}
							<div class="message-status">
								{#if message.status === 'pending'}
									<div class="status-indicator pending">
										<div class="spinner"></div>
										<span>Sending...</span>
									</div>
								{:else if message.status === 'sent'}
									<div class="status-indicator sent">
										<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
											<polyline points="20,6 9,17 4,12"></polyline>
										</svg>
									</div>
								{:else if message.status === 'error'}
									<div class="status-indicator error">
										<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
											<circle cx="12" cy="12" r="10"></circle>
											<line x1="15" y1="9" x2="9" y2="15"></line>
											<line x1="9" y1="9" x2="15" y2="15"></line>
										</svg>
									</div>
								{/if}
							</div>
						{/if}
						
						{#if message.projectPlan}
							<div class="project-plan">
								<div class="plan-section">
									<h3>📋 Project Overview</h3>
									<p>{message.projectPlan.projectOverview}</p>
								</div>

								<div class="plan-section">
									<h3>🛠️ Tech Stack</h3>
									<div class="tech-stack">
										{#each message.projectPlan.techStack as tech}
											<span class="tech-badge">{tech}</span>
										{/each}
									</div>
								</div>

							<div class="plan-section">
								<h3>📅 Timeline</h3>
								{#each message.projectPlan.timeline as block, blockIndex}
									<div class="time-block">
										<h4>{block.timeBlock}</h4>
										<ul>
											{#each block.tasks as task, taskIndex}
												<li class:essential={task.essential} class:completed={task.completed}>
													<input 
														type="checkbox" 
														checked={task.completed}
														on:change={() => toggleTaskCompletion(message.conversationId!, blockIndex, taskIndex, task.completed)}
														class="task-checkbox"
													/>
													<span class="task-name">{@html renderMarkdown(task.task)}</span>
													<span class="task-time">{task.estimatedTime}</span>
													{#if task.essential}
														<span class="essential-badge">Essential</span>
													{/if}
												</li>
											{/each}
										</ul>
									</div>
								{/each}
							</div>								<div class="plan-section">
									<h3>💡 Tips</h3>
									<ul class="tips-list">
										{#each message.projectPlan.tips as tip}
											<li>{tip}</li>
										{/each}
									</ul>
								</div>
							</div>
						{/if}
					</div>
				</div>
			{/each}
		{/if}
	</div>

	<div class="input-container">
		<!-- Mode selector -->
		<div class="mode-selector">
			<label class="mode-label">Planning Mode:</label>
			<div class="mode-options">
				<label class="mode-option">
					<input 
						type="radio" 
						bind:group={planningMode} 
						value="basic"
						disabled={isSending}
					/>
					<span class="mode-text">
						<strong>Basic</strong>
						<small>Quick, concise tasks</small>
					</span>
				</label>
				<label class="mode-option">
					<input 
						type="radio" 
						bind:group={planningMode} 
						value="detailed"
						disabled={isSending}
					/>
					<span class="mode-text">
						<strong>Detailed</strong>
						<small>Ultra-specific with code & commands</small>
					</span>
				</label>
			</div>
		</div>
		
		<div class="input-section">
			<textarea 
				bind:value={inputValue}
				on:keydown={handleKeydown}
				placeholder="Tell me what app you want to plan this weekend..."
				disabled={isSending}
				rows="3"
			></textarea>
			<button on:click={sendMessage} disabled={isSending || !inputValue.trim()}>
				{isSending ? 'Sending...' : 'Send'}
			</button>
		</div>
		</div>
	</main>
</div>

<style lang="scss">
	@import './assets/chat.scss';
</style>
