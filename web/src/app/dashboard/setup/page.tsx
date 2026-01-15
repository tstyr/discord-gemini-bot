'use client'

import { motion } from 'framer-motion'
import Card from '@/components/Card'
import { 
  Zap, 
  Globe, 
  Lock, 
  MessageSquare, 
  Users, 
  Shield,
  ArrowRight,
  CheckCircle,
  Copy,
  ExternalLink
} from 'lucide-react'
import { useState } from 'react'

export default function SetupPage() {
  const [copiedCommand, setCopiedCommand] = useState<string>('')

  const copyCommand = (command: string) => {
    navigator.clipboard.writeText(command)
    setCopiedCommand(command)
    setTimeout(() => setCopiedCommand(''), 2000)
  }

  const commands = [
    {
      command: '/setup-public-chat',
      title: 'パブリックAIチャンネル作成',
      description: '全メンバーがアクセスできるAI専用チャンネルを作成します',
      icon: Globe,
      color: 'text-osu-cyan',
      bgColor: 'bg-osu-cyan/20',
      features: [
        '全メンバーが読み書き可能',
        'AI-CHATカテゴリーに作成',
        '#gemini-public チャンネル',
        '自動応答機能有効'
      ]
    },
    {
      command: '/setup-private-chat',
      title: 'プライベートAIチャンネル作成',
      description: 'あなた専用のプライベートAIチャンネルを作成します',
      icon: Lock,
      color: 'text-osu-purple',
      bgColor: 'bg-osu-purple/20',
      features: [
        '実行者のみアクセス可能',
        '管理者も閲覧可能',
        '#chat-with-[ユーザー名] 形式',
        '完全プライベート環境'
      ]
    }
  ]

  return (
    <div className="min-h-screen bg-osu-dark relative overflow-hidden">
      {/* Background decorations */}
      <div className="absolute top-0 left-1/4 w-96 h-96 bg-osu-pink/5 rounded-full blur-3xl" />
      <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-osu-cyan/5 rounded-full blur-3xl" />
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full h-0.5 bg-gradient-to-r from-transparent via-osu-purple/20 to-transparent rotate-12" />

      <div className="relative z-10 p-8">
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="mb-8"
        >
          <h1 className="text-4xl font-bold text-white mb-2 flex items-center gap-3">
            <Zap className="w-8 h-8 text-osu-pink" />
            AIチャンネル セットアップ
          </h1>
          <p className="text-gray-400">
            Discord でスラッシュコマンドを使用してAI専用チャンネルを作成しましょう
          </p>
        </motion.div>

        {/* Setup Guide */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {commands.map((cmd, index) => {
            const Icon = cmd.icon
            
            return (
              <Card key={cmd.command} delay={0.1 + index * 0.1}>
                <div className="mb-6">
                  <div className="flex items-center gap-3 mb-4">
                    <div className={`p-3 rounded-xl ${cmd.bgColor}`}>
                      <Icon className={`w-6 h-6 ${cmd.color}`} />
                    </div>
                    <div>
                      <h2 className="text-xl font-semibold text-white">{cmd.title}</h2>
                      <p className="text-gray-400 text-sm">{cmd.description}</p>
                    </div>
                  </div>

                  {/* Command */}
                  <div className="bg-osu-darker border border-osu-border rounded-lg p-4 mb-4">
                    <div className="flex items-center justify-between">
                      <code className="text-osu-pink font-mono text-lg">{cmd.command}</code>
                      <motion.button
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        onClick={() => copyCommand(cmd.command)}
                        className="flex items-center gap-2 px-3 py-1 bg-osu-pink/20 text-osu-pink rounded-lg hover:bg-osu-pink/30 transition-colors duration-200"
                      >
                        {copiedCommand === cmd.command ? (
                          <>
                            <CheckCircle className="w-4 h-4" />
                            <span className="text-sm">コピー済み</span>
                          </>
                        ) : (
                          <>
                            <Copy className="w-4 h-4" />
                            <span className="text-sm">コピー</span>
                          </>
                        )}
                      </motion.button>
                    </div>
                  </div>

                  {/* Features */}
                  <div className="space-y-2">
                    {cmd.features.map((feature, featureIndex) => (
                      <motion.div
                        key={featureIndex}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ duration: 0.3, delay: 0.2 + featureIndex * 0.1 }}
                        className="flex items-center gap-2 text-gray-300"
                      >
                        <CheckCircle className="w-4 h-4 text-green-500" />
                        <span className="text-sm">{feature}</span>
                      </motion.div>
                    ))}
                  </div>
                </div>

                <div className="pt-4 border-t border-osu-border">
                  <div className="flex items-center gap-2 text-gray-400 text-sm">
                    <Shield className="w-4 h-4" />
                    <span>チャンネル管理権限が必要です</span>
                  </div>
                </div>
              </Card>
            )
          })}
        </div>

        {/* Step by Step Guide */}
        <Card delay={0.3}>
          <h2 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-osu-cyan" />
            セットアップ手順
          </h2>

          <div className="space-y-6">
            {[
              {
                step: 1,
                title: 'Discordサーバーにアクセス',
                description: 'AIボットが導入されているDiscordサーバーに移動します',
                icon: ExternalLink
              },
              {
                step: 2,
                title: 'スラッシュコマンドを実行',
                description: '上記のコマンドをチャットで入力して実行します',
                icon: MessageSquare
              },
              {
                step: 3,
                title: 'チャンネル作成を待機',
                description: 'ボットが自動的にカテゴリーとチャンネルを作成します',
                icon: Zap
              },
              {
                step: 4,
                title: 'AIとの会話開始',
                description: '作成されたチャンネルでAIとの会話を楽しみましょう',
                icon: Users
              }
            ].map((step, index) => {
              const Icon = step.icon
              
              return (
                <motion.div
                  key={step.step}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.3, delay: 0.4 + index * 0.1 }}
                  className="flex items-start gap-4 p-4 bg-osu-darker rounded-lg"
                >
                  <div className="flex-shrink-0 w-8 h-8 bg-osu-gradient rounded-full flex items-center justify-center text-white font-bold text-sm">
                    {step.step}
                  </div>
                  
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <Icon className="w-5 h-5 text-osu-pink" />
                      <h3 className="text-white font-medium">{step.title}</h3>
                    </div>
                    <p className="text-gray-400 text-sm">{step.description}</p>
                  </div>
                  
                  {index < 3 && (
                    <ArrowRight className="w-5 h-5 text-gray-600 mt-2" />
                  )}
                </motion.div>
              )
            })}
          </div>
        </Card>

        {/* Tips */}
        <Card delay={0.4} className="mt-8">
          <h2 className="text-xl font-semibold text-white mb-4 flex items-center gap-2">
            <Shield className="w-5 h-5 text-osu-purple" />
            重要な注意事項
          </h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <h3 className="text-white font-medium">権限について</h3>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>パブリックチャンネル作成には「チャンネル管理」権限が必要</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>プライベートチャンネルは誰でも作成可能</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                  <span>管理者は全てのプライベートチャンネルにアクセス可能</span>
                </li>
              </ul>
            </div>
            
            <div className="space-y-3">
              <h3 className="text-white font-medium">使用上の注意</h3>
              <ul className="space-y-2 text-gray-400 text-sm">
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                  <span>同じ名前のチャンネルが既に存在する場合は作成されません</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                  <span>プライベートチャンネルは1ユーザーにつき1つまで</span>
                </li>
                <li className="flex items-start gap-2">
                  <CheckCircle className="w-4 h-4 text-yellow-500 mt-0.5 flex-shrink-0" />
                  <span>チャンネル削除はWebダッシュボードから可能</span>
                </li>
              </ul>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}