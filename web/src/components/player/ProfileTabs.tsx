import { useState } from 'react'
import { Tabs, TabsList, TabsTrigger, TabsContent } from '@/components/ui/tabs'

interface ProfileTabsProps {
  mainContent: React.ReactNode
  friendsContent?: React.ReactNode
  photosContent?: React.ReactNode
  venuesContent?: React.ReactNode
}

export const ProfileTabs = ({ mainContent, friendsContent, photosContent, venuesContent }: ProfileTabsProps) => {
  const [activeTab, setActiveTab] = useState('main')

  return (
    <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
      <TabsList className="grid w-full grid-cols-4">
        <TabsTrigger value="main">Principal</TabsTrigger>
        <TabsTrigger value="friends">Amigos</TabsTrigger>
        <TabsTrigger value="photos">Fotos</TabsTrigger>
        <TabsTrigger value="venues">Onde Joga</TabsTrigger>
      </TabsList>

      <TabsContent value="main" className="mt-6">
        {mainContent}
      </TabsContent>

      <TabsContent value="friends" className="mt-6">
        {friendsContent || (
          <div className="text-center py-12 text-muted-foreground">
            Lista de amigos em desenvolvimento
          </div>
        )}
      </TabsContent>

      <TabsContent value="photos" className="mt-6">
        {photosContent || (
          <div className="text-center py-12 text-muted-foreground">
            Galeria de fotos em desenvolvimento
          </div>
        )}
      </TabsContent>

      <TabsContent value="venues" className="mt-6">
        {venuesContent || (
          <div className="text-center py-12 text-muted-foreground">
            Locais de jogo em desenvolvimento
          </div>
        )}
      </TabsContent>
    </Tabs>
  )
}
