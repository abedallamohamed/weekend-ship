<script lang="ts">
	export let isOpen = true;
	
	// Simulate previous chat sessions
	const previousChats = [
		{ id: 1, title: "Active Chat", date: "10 seconds ago", active: true },
		{ id: 2, title: "Recipe Sharing App", date: "2 hours ago" },
		{ id: 3, title: "Task Manager with AI", date: "Yesterday" },
		{ id: 4, title: "Personal Finance Tracker", date: "2 days ago" },
		{ id: 5, title: "Weather Dashboard", date: "3 days ago" },
		{ id: 6, title: "Chat Application", date: "1 week ago" }
	];
	
	function toggleSidebar() {
		isOpen = !isOpen;
	}
	
	function selectChat(chatId: number) {
		// Update active chat
		previousChats.forEach(chat => chat.active = chat.id === chatId);
	}
	
	function startNewChat() {
		// TODO: Communicate with parent to start a new chat
        
	}
</script>

<aside class="sidebar" class:collapsed={!isOpen}>
	<div class="sidebar-header">
		<h2>Weekend Ship</h2>
		<button class="sidebar-toggle" on:click={toggleSidebar}>
			<svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
				<path d="M3 12h18M3 6h18M3 18h18"/>
			</svg>
		</button>
	</div>
	
	<nav class="sidebar-nav">
		<div class="nav-section">
			<div class="section-header">
				<h3>Recent Projects</h3>
				<button class="new-chat-btn" on:click={startNewChat}>
					<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
						<path d="M12 5v14M5 12h14"/>
					</svg>
				</button>
			</div>
			<ul class="chat-list">
				{#each previousChats as chat (chat.id)}
					<li class="chat-item" class:active={chat.active} on:click={() => selectChat(chat.id)}>
						<div class="chat-icon">
							<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
								<path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
							</svg>
						</div>
						<div class="chat-details">
							<span class="chat-title">{chat.title}</span>
							<span class="chat-date">{chat.date}</span>
						</div>
					</li>
				{/each}
			</ul>
		</div>
	</nav>
</aside>

<style lang="scss">
	@import './sidebar.scss';
</style>