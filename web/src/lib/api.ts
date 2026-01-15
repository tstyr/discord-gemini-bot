const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export interface Stats {
  total_messages: number
  total_tokens: number
  unique_users: number
  avg_tokens: number
}

export interface Guild {
  id: string
  name: string
  member_count: number
  icon: string | null
}

export interface Channel {
  id: string
  name: string
  category: string | null
  ai_enabled: boolean
}

export interface ApiResponse<T> {
  success: boolean
  data?: T
  message?: string
}

class ApiClient {
  private async request<T>(endpoint: string, options?: RequestInit): Promise<ApiResponse<T>> {
    try {
      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        headers: {
          'Content-Type': 'application/json',
          ...options?.headers,
        },
        ...options,
      })

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error)
      return { success: false, message: 'API request failed' }
    }
  }

  // Health check
  async healthCheck() {
    return this.request('/api/health')
  }

  // Stats
  async getStats(guildId?: string): Promise<ApiResponse<Stats>> {
    const params = guildId ? `?guild_id=${guildId}` : ''
    return this.request<Stats>(`/api/stats${params}`)
  }

  // Chat logs
  async getChatLogs(guildId?: string, limit: number = 50) {
    const params = new URLSearchParams()
    if (guildId) params.append('guild_id', guildId)
    params.append('limit', limit.toString())
    
    return this.request(`/api/chat-logs?${params.toString()}`)
  }

  // Cost optimization
  async getCostUsage() {
    return this.request('/api/cost/usage')
  }

  async getSimpleResponses() {
    return this.request('/api/cost/simple-responses')
  }

  // Guilds
  async getGuilds(): Promise<ApiResponse<Guild[]>> {
    return this.request<Guild[]>('/api/guilds')
  }

  async getGuildChannels(guildId: string): Promise<ApiResponse<Channel[]>> {
    return this.request<Channel[]>(`/api/guilds/${guildId}/channels`)
  }

  // AI Mode
  async getAiMode(guildId: string) {
    return this.request(`/api/guilds/${guildId}/mode`)
  }

  async setAiMode(guildId: string, mode: string) {
    return this.request('/api/mode', {
      method: 'POST',
      body: JSON.stringify({ guild_id: parseInt(guildId), mode }),
    })
  }

  // Channel management
  async toggleChannel(guildId: string, channelId: string, enable: boolean) {
    return this.request('/api/channels/toggle', {
      method: 'POST',
      body: JSON.stringify({
        guild_id: parseInt(guildId),
        channel_id: parseInt(channelId),
        enable,
      }),
    })
  }

  // Music Player
  async getMusicStatus(guildId: string) {
    return this.request(`/api/guilds/${guildId}/music/status`)
  }

  async controlMusic(guildId: string, action: string) {
    return this.request(`/api/guilds/${guildId}/music/control?action=${action}`, {
      method: 'POST'
    })
  }

  async setPlaybackMode(guildId: string, mode: 'discord' | 'web') {
    return this.request(`/api/guilds/${guildId}/music/playback-mode?mode=${mode}`, {
      method: 'POST'
    })
  }

  async getStreamUrl(trackUri: string) {
    return this.request(`/api/stream/${encodeURIComponent(trackUri)}`)
  }

  async getAIEQSettings(genre: string) {
    return this.request(`/api/ai/eq-settings/${encodeURIComponent(genre)}`)
  }

  // AI Channels management
  async getAiChannels(guildId: string) {
    return this.request(`/api/guilds/${guildId}/ai-channels`)
  }

  async deleteChannel(channelId: string, guildId: string) {
    return this.request(`/api/channels/${channelId}?guild_id=${guildId}`, {
      method: 'DELETE'
    })
  }

  async getChannelActivity(guildId: string) {
    return this.request(`/api/guilds/${guildId}/channel-activity`)
  }

  // WebSocket connection for real-time updates
  connectWebSocket(onMessage: (data: any) => void) {
    const wsUrl = API_BASE_URL.replace('http', 'ws') + '/ws'
    const ws = new WebSocket(wsUrl)
    
    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        onMessage(data)
      } catch (error) {
        console.error('WebSocket message parse error:', error)
      }
    }
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error)
    }
    
    return ws
  }
}

export const apiClient = new ApiClient()