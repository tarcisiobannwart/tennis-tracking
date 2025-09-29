import { useState, useRef } from 'react'
import { Upload, X, Play, FileVideo } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { uploadFile } from '@/services/api'

interface VideoUploadModalProps {
  isOpen: boolean
  onClose: () => void
  onUploadSuccess?: (data: any) => void
}

const VideoUploadModal = ({ isOpen, onClose, onUploadSuccess }: VideoUploadModalProps) => {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const [progress, setProgress] = useState(0)
  const [dragOver, setDragOver] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  if (!isOpen) return null

  const handleFileSelect = (file: File) => {
    // Validar tipo de arquivo
    const validTypes = ['video/mp4', 'video/avi', 'video/mov', 'video/quicktime', 'video/x-msvideo']
    if (!validTypes.includes(file.type)) {
      alert('Formato não suportado. Use MP4, AVI ou MOV.')
      return
    }

    // Validar tamanho (max 500MB)
    const maxSize = 500 * 1024 * 1024
    if (file.size > maxSize) {
      alert('Arquivo muito grande. Máximo 500MB.')
      return
    }

    setSelectedFile(file)
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    setDragOver(false)

    const files = Array.from(e.dataTransfer.files)
    if (files.length > 0) {
      handleFileSelect(files[0])
    }
  }

  const handleUpload = async () => {
    if (!selectedFile) return

    setUploading(true)
    setProgress(0)

    try {
      const result = await uploadFile(
        '/upload/video',
        selectedFile,
        (progressPercent) => {
          setProgress(progressPercent)
        }
      )

      console.log('Upload successful:', result)
      onUploadSuccess?.(result)
      onClose()
      setSelectedFile(null)
    } catch (error) {
      console.error('Upload failed:', error)
      alert('Erro no upload. Tente novamente.')
    } finally {
      setUploading(false)
      setProgress(0)
    }
  }

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="w-full max-w-md mx-4">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center">
              <Upload className="w-5 h-5 mr-2" />
              Upload de Vídeo
            </CardTitle>
            <Button variant="ghost" size="sm" onClick={onClose}>
              <X className="w-4 h-4" />
            </Button>
          </div>
        </CardHeader>
        <CardContent className="space-y-4">
          {!selectedFile ? (
            <>
              {/* Drop Zone */}
              <div
                className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
                  dragOver ? 'border-primary bg-primary/5' : 'border-muted-foreground/25'
                }`}
                onDrop={handleDrop}
                onDragOver={(e) => {
                  e.preventDefault()
                  setDragOver(true)
                }}
                onDragLeave={() => setDragOver(false)}
                onClick={() => fileInputRef.current?.click()}
              >
                <FileVideo className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-lg font-medium mb-2">
                  Arraste o vídeo aqui
                </p>
                <p className="text-sm text-muted-foreground mb-4">
                  ou clique para selecionar
                </p>
                <Button variant="outline">
                  Selecionar Arquivo
                </Button>
              </div>

              <input
                ref={fileInputRef}
                type="file"
                accept=".mp4,.avi,.mov,.mkv,.wmv"
                onChange={(e) => {
                  const file = e.target.files?.[0]
                  if (file) handleFileSelect(file)
                }}
                className="hidden"
              />

              <div className="text-xs text-muted-foreground">
                <p>Formatos suportados: MP4, AVI, MOV, MKV, WMV</p>
                <p>Tamanho máximo: 500MB</p>
              </div>
            </>
          ) : (
            <>
              {/* File Info */}
              <div className="border rounded-lg p-4">
                <div className="flex items-center space-x-3">
                  <FileVideo className="w-8 h-8 text-blue-500" />
                  <div className="flex-1 min-w-0">
                    <p className="font-medium truncate">{selectedFile.name}</p>
                    <p className="text-sm text-muted-foreground">
                      {formatFileSize(selectedFile.size)}
                    </p>
                  </div>
                  {!uploading && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => setSelectedFile(null)}
                    >
                      <X className="w-4 h-4" />
                    </Button>
                  )}
                </div>

                {uploading && (
                  <div className="mt-4">
                    <div className="flex justify-between text-sm mb-2">
                      <span>Enviando...</span>
                      <span>{Math.round(progress)}%</span>
                    </div>
                    <div className="w-full bg-secondary rounded-full h-2">
                      <div
                        className="bg-primary h-2 rounded-full transition-all"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                  </div>
                )}
              </div>

              {/* Actions */}
              <div className="flex space-x-2">
                <Button
                  onClick={handleUpload}
                  disabled={uploading}
                  className="flex-1"
                >
                  <Play className="w-4 h-4 mr-2" />
                  {uploading ? 'Enviando...' : 'Iniciar Análise'}
                </Button>
                <Button
                  variant="outline"
                  onClick={onClose}
                  disabled={uploading}
                >
                  Cancelar
                </Button>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default VideoUploadModal