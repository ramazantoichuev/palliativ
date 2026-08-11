from modeltranslation.translator import TranslationOptions, translator

from news.models.posts import Post, Category

class PostTranslationOptions(TranslationOptions):
    fields = ('title', 'content')

class CategoryTranslationOptions(TranslationOptions):
    fields = ('title',)

translator.register(Post, PostTranslationOptions)
translator.register(Category, CategoryTranslationOptions)