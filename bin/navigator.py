from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from pods.models import Pod
from filer.models.foldermodels import Folder
from filer.models.imagemodels  import Image
from django.core.files import File
from core.models import get_media_guard, EncodingType
import os

DEVNULL=None

import os

class Navigator():

    def cdrel(self,name):
        self.wd, _ = Folder.objects.get_or_create\
            ( name=name
            , owner=self.wd.owner
            , parent=self.wd )
        return self.wd

    def cdpk(self,pk): self.wd = Folder.objects.get(id=int(pk))

    def go_home(self,owner):
        self.wd = Folder.objects.get\
            ( name=owner
            , owner=owner
            , level=0 )

    def go_video_slug(self,video):
        self.go_home(video.owner)
        return self.cdrel(video.slug)

    def store(self,model,source,dest):
        file, DEVNULL = model.objects.get_or_create\
            ( folder = self.wd
            , name   = dest
            , owner  = self.wd.owner )
        os.rename(source, file.path)
        return file

    def pwd(self):
        p = self.wd
        for i in [ p.name, p.pk, p.pretty_logical_path ]: print(i)

def V(v):
    if isinstance(v,Pod): return v
    if isinstance(v,str): return Pod.objects.get(id=v)
    return None

def ressources_root_for(video):
    video = V(video)
    login = video.owner.username
    id    = video.id
    return os.path.join\
        ( settings.MEDIA_ROOT
        , getattr(settings,'VIDEOS_DIR','video')
        , login
        , get_media_guard( login, id )
        , "%s" % id )

def get_video_scales():
    return [ e.output_height
        for e in EncodingType.objects.filter(mediatype='video') ]

class Command(BaseCommand):
    args = '<video t t ...>'
    help = 'Encodes the specified content.'

    def set_thumbnails(self,video,*ts):
        video = V(video)
        store = Navigator()
        store.go_video_slug(video)
        thumbnails =\
            [ store.store( Image, t, "%d_%s.png" % (video.id, i) )
                for i,t in enumerate(ts) ]
        for t in thumbnails: t.save()
        video.thumbnail = thumbnails[1]
        video.save()

    def ressources_root_for(self,video): print(ressources_root_for(video))

    def get_video_scales(self):
        for e in get_video_scales(): print(e)

    def set_video_overview(self,video,filename):
        video = V(video)
        video.overview = filename
        video.save()

    def add_encoding_for(self,video,height,filename):
        video = V(video)
        epod  = EncodingPods.objects.get_or_create\
            ( video=video
            , encodingType=
                EncodingType.objects.filter\
                    ( mediatype='video'
                    , output_height=height )
            , encodingFormat="video/mp4")
        epod.encodingFile = filename
        epod.save()
        video.save()

    def handle(self, *args, **options): getattr(self,args[0])(*args[1:])