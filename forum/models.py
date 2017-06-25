#coding:utf-8
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.db.models import signals
import datetime

# Create your models here.

class LoginUser(AbstractUser):
    levels = models.PositiveIntegerField(default=0,verbose_name=u'积分')
    avatar = models.CharField(max_length=200,default='/static/tx/default.jpg',verbose_name=u'头像')
    privilege = models.CharField(max_length=200,default=0,verbose_name=u'权限')
    friends = models.ManyToManyField('self', blank=True, null=True,related_name='friends')

    class Meta:
        db_table = 'loginuser'
        verbose_name_plural = u'用户'
        ordering = ['-date_joined']

    def __unicode__(self):
        return self.get_username()

    def checkfriend(self,username):
        if username in self.friends.all():
            return True
        else:
            return False

class Nav(models.Model):
    name = models.CharField(max_length=40,verbose_name=u'导航条')
    url = models.CharField(max_length=200,blank=True,null=True,verbose_name=u'指向地址')
    create_time = models.DateTimeField(u'创建时间',default=datetime.datetime.now,auto_now_add=True)

    class Meta:
        db_table = 'nav'
        verbose_name_plural = verbose_name = u"导航条"
        ordering = ['-create_time']

    def __unicode__(self):
        return self.name    

class Column(models.Model):							#板块
    name = models.CharField(max_length=30)
    manager = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='column_manager')							#版主
    parent = models.ForeignKey('self', blank=True, null=True,related_name='childcolumn')
    description = models.TextField()
    img = models.CharField(max_length=200,default='/static/tx/default.jpg',verbose_name=u'图标')
    post_number = models.IntegerField(default=0) 	#主题数
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
   
    class Meta:
        db_table = 'column'
        ordering = ['-post_number']
        verbose_name_plural = u'板块'
        
    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('column_detail', (), { 'column_pk': self.pk })
        
class PostType(models.Model):			#文章类型
    type_name = models.CharField(max_length=30)
    description = models.TextField()
    created_at = models.DateTimeField(default=datetime.datetime.now)
    class Meta:
        db_table = 'posttype'
        verbose_name_plural = u'主题类型'
    def __unicode__(self):
        return self.type_name

class Post(models.Model):					#文章
    title = models.CharField(max_length=30)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='post_author')				#作者
    column = models.ForeignKey(Column)						#所属板块
    type_name = models.ForeignKey(PostType)						#文章类型
    content = models.TextField()
    
    view_times = models.IntegerField(default=0)		#浏览次数
    responce_times = models.IntegerField(default=0)		#回复次数
    last_response = models.ForeignKey(settings.AUTH_USER_MODEL)							#最后回复者
    
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    
    
    class Meta:
        db_table = 'post'
        ordering = ['-created_at']
        verbose_name_plural = u'主题'
        
    def __unicode__(self):
        return self.title
    
    def description(self):
        return u'%s 发表了主题《%s》' % (self.author, self.title)
    
    @models.permalink
    def get_absolute_url(self):
        return ('post_detail', (), {'post_pk': self.pk })
        
       
class Comment(models.Model):				#评论	
    post = models.ForeignKey(Post)						
    author = models.ForeignKey(settings.AUTH_USER_MODEL)						
    comment_parent = models.ForeignKey('self', blank=True, null=True,related_name='childcomment')						
    content = models.TextField()
   
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    
    class Meta:
        db_table = 'comment'
        ordering = ['created_at']
        verbose_name_plural = u'评论'
        
    def __unicode__(self):
        return self.content

    def description(self):
        return u'%s 回复了您的帖子(%s) R:《%s》' % (self.author,self.post, self.content)
    
    @models.permalink
    def get_absolute_url(self):
        return ('post_detail', (), { 'post_pk': self.post.pk })
        
class Message(models.Model):			#好友消息
    sender = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='message_sender')							#发送者
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='message_receiver')						#接收者
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    
    def description(self):
        return u'%s 给你发送了消息《%s》' % (self.sender, self.content)

    class Meta:
        db_table = 'message'
        verbose_name_plural = u'消息'
    
class Application(models.Model):			#好友申请
    sender = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='appli_sender')							#发送者
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='appli_receiver')						#接收者
    status = models.IntegerField(default=0)				#申请状态 0:未查看 1:同意 2:不同意
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    def description(self):
        return u'%s 申请加好友' % self.sender   

    class Meta:
        db_table = 'application'
        verbose_name_plural = u'好友申请'
    
class Notice(models.Model):
    sender = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='notice_sender')							#发送者
    receiver = models.ForeignKey(settings.AUTH_USER_MODEL,related_name='notice_receiver')						#接收者
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    event = generic.GenericForeignKey('content_type', 'object_id')
    
    status = models.BooleanField(default=False)		#是否阅读
    type = models.IntegerField()					#通知类型 0:评论 1:好友消息 2:好友申请
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    
    class Meta:
        db_table = 'notice'
        ordering = ['-created_at']
        verbose_name_plural = u'通知'
    
    def __unicode__(self):
        return  u"%s的事件: %s" % (self.sender, self.description())

    def description(self):
        if self.event:
          return self.event.description()
        return "No Event"
        
    def reading(self):
        if not status:
            status = True

def post_save(sender, instance, signal, *args, **kwargs):
    entity = instance
    if str(entity.created_at)[:19] == str(entity.updated_at)[:19]: #第一次发帖操作，编辑不操作
        column = entity.column
        column.post_number += 1
        column.save()

def post_delete(sender, instance, signal, *args, **kwargs):	#删帖触发板块帖子数减1
    entity = instance
    column = entity.column
    column.post_number -= 1
    column.save()
    
    
def comment_save(sender, instance, signal, *args, **kwargs):    
    entity = instance
    if str(entity.created_at)[:19] == str(entity.updated_at)[:19]: 
    	if entity.author != entity.post.author:                       #作者的回复不给作者通知
            event = Notice(sender=entity.author,receiver=entity.post.author,event = entity,type=0) 
            event.save()
        if entity.comment_parent is not None:		              #回复评论给要评论的人通知
            if entity.author.id != entity.comment_parent.author.id:   #自己给自己写评论不通知
                event = Notice(sender=entity.author,receiver=entity.comment_parent.author,event = entity,type=0) 
                event.save()

def application_save(sender, instance, signal, *args, **kwargs):
    entity = instance
    if str(entity.created_at)[:19] == str(entity.updated_at)[:19]: 
        event = Notice(sender=entity.sender,receiver=entity.receiver,event = entity,type=1) 
        event.save()
  
def message_save(sender, instance, signal, *args, **kwargs):
    entity = instance
    if str(entity.created_at)[:19] == str(entity.updated_at)[:19]: 
        event = Notice(sender=entity.sender,receiver=entity.receiver,event = entity,type=2) 
        event.save()


#消息响应函数注册
signals.post_save.connect(comment_save, sender=Comment)
signals.post_save.connect(application_save, sender=Message)
signals.post_save.connect(message_save, sender=Application)
signals.post_save.connect(post_save, sender=Post)
signals.post_delete.connect(post_delete, sender=Post)
