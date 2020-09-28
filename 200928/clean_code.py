# ----------monostate pattern------------

class GitFetcher:
    _current_tag = None

    def __init__(self, tag):
        self.current_tag = tag

    @property
    def current_tag(self):
        if self._current_tag is None:
            raise AttributeError('tag가 초기화되지 않음')
        return self._current_tag

    @current_tag.setter
    def current_tag(self, new_tag):
        self.__class__._current_tag = new_tag

    def pull(self):
        print(f"{self.current_tag}에서 풀")
        return self.current_tag


# feature_1 = GitFetcher(0.1)
# print(feature_1.current_tag)  # 0.1
# print(vars(feature_1))  # {}
# feature_2 = GitFetcher(0.2)
# print(feature_2.current_tag)  # 0.2
# print(vars(feature_1))  # {}
#
# feature_1.current_tag = 'develop'
#
# print(feature_1.pull())  # develop
# print(feature_2.pull())  # develop
#

class GitFetcher1:
    current_tag = 'develop'


# feature_1 = GitFetcher1()
# feature_2 = GitFetcher1()
# print(feature_1.current_tag)
# print(feature_2.current_tag)


# ---------- gitfetcher with descriptor ------------
class SharedAttribute:
    def __init__(self, initial_value=None):
        self.value = initial_value
        self._name = None

    def __set_name__(self, owner, name):
        self._name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        if self.value is None:
            raise AttributeError(f"{self._name}가 초기화 안됨")
        return self.value

    def __set__(self, instance, value):
        self.value = value


class GitFetcherWithDescriptor:
    current_tag = SharedAttribute()
    current_branch = SharedAttribute()

    def __init__(self, tag=None, branch=None):
        self.current_tag = tag
        self.current_branch = branch

    def pull(self):
        print(f"{self.current_tag}에서 풀")
        return self.current_tag


# feature_1 = GitFetcherWithDescriptor(0.1, 'master')
# print(vars(feature_1))
# print(feature_1.current_tag)  # 0.1
# print(feature_1.current_branch)  # master
# feature_2 = GitFetcherWithDescriptor(0.2, 'develop')
# print(feature_2.current_tag)  # 0.2
# print(feature_2.current_branch)  # develop
# print(feature_1.current_tag)  # 0.2
# print(feature_1.current_branch)  # develop
#
# feature_2.current_tag = 0.0
# print(feature_2.current_tag)  # 0.0
# print(feature_1.current_tag)  # 0.0
# print(vars(feature_1))
# print(dir(feature_1))
# --------- borg ---------------
class SharedAllMixin:
    def __init__(self, *args, **kwargs):
        try:
            self.__class__._attributes
        except AttributeError:
            self.__class__._attributes = {}

        self.__dict__ = self.__class__._attributes
        super(SharedAllMixin, self).__init__(*args, **kwargs)


class BaseFetcher:
    def __init__(self, source):
        self.source = source


class TagFetcher(SharedAllMixin, BaseFetcher):
    def pull(self):
        print(f"{self.source}에서 풀")
        return f"Tag = {self.source}"


class Branch(SharedAllMixin, BaseFetcher):
    def pull(self):
        print(f"{self.source}에서 풀")
        return f"Branch = {self.source}"


tf1 = TagFetcher("tag1")
tf2 = TagFetcher("tag2")
tf3 = TagFetcher("tag3")
print(tf1.pull())
print(tf1._attributes)
print(dir(tf1))
print(vars(tf1))
