#-*- coding:utf-8 -*-
##################################################################
# Author : zcx
# Date   : 2023.12
# Email  : 978654313@qq.com
# version: 3.9.7
##################################################################
import time
import os
from PIL import Image, ImageOps
import json
import string
import UnrealPipeline.core.UnrealHelper as UH
import random
import shutil


from .backend import Backend

if Backend.Get().isBackendAvailable():
    category = Backend.Get().getCategories()
else:
    category = {}

def GetParentsCategory(name):
    for p in category.keys():
        for c in category[p].keys():
            for cc in category[p][c]:
                if name == cc:
                    return p,c,cc
    return False

def GetCategorys(level:int):
    if level == 0:
        return list(category.keys())
    elif level == 1:
        return [ele for value in category.values() for ele in value.keys() ]
    elif level == 2:
        return [c for value in category.values() for ele in value.keys() for c in value[ele]]
    else:
        raise
def GetSubCategorys(parentIndex:int):
    return [ele for ele in category[GetCategorys(0)[parentIndex]].keys()]

CameraPathMacros = [
    "$ep",
    "$sc",
    "$number",
    "$frameStart",
    "$frameEnd",
    "$fullName",
]

StaticMeshMacros = [
    "$name",
    "$scenename"
]

CameraHeader = [
    {
        "label": "文件名称",
        "key": "name",
        "checkable": False,
        "searchable": True,
    },
    {
        "label": "修改日期",
        "key": "modifyTime",
        "checkable": False,
        "searchable": False,

    },
        {
        "label": "文件大小",
        "key": "size",
        "checkable": False,
        "searchable": False,
    },
    {
        "label": "路径",
        "key": "path",
        "checkable": False,
        "searchable": False,
    },
]

#classes
class ConvertTexture:
    def __init__(self,TextureDict,TextureSize) -> None:
        self.TextureDict = TextureDict
        self.TextureSize = (TextureSize,TextureSize)

    # 将RedshiftMaterial转换为ARMS
    def ConvertMTextureToARMS(self):
        # 判断给定的贴图列表的漫反射颜色是否不存在贴图，如果不存在就返回假
        if self.TextureDict['diffuse_color'] == None:
            return False
        TextureCount = len(self.TextureDict['diffuse_color'])

        refl_roughness_Texturelist     = self.TextureDict['refl_roughness']
        diffuse_color_Texturelist      = self.TextureDict['diffuse_color']
        refl_color_Texturelist         = self.TextureDict['refl_color']
        bump_input_Texturelist         = self.TextureDict['bump_input']
        refl_reflectivity_Texturelist  = self.TextureDict['refl_reflectivity']
        refl_metalness_Texturelist     = self.TextureDict['refl_metalness']
        if refl_reflectivity_Texturelist  != refl_metalness_Texturelist :
            if refl_reflectivity_Texturelist  != None:
                MetallicPathList = refl_reflectivity_Texturelist 
            else:
                MetallicPathList = refl_metalness_Texturelist 
        else:
            MetallicPathList = None
        NewNormalPathList = []
        ARMSPathList = []
        BaseColorPathList = []
        ConvetBaseColor = True
        for i in range(0,TextureCount):
            DiffuseTexture = Image.open(diffuse_color_Texturelist[i]).resize(self.TextureSize)
            try:
                refl_roughness_Texture_Path = refl_roughness_Texturelist[i]
                refl_roughness_Texture = Image.open(refl_roughness_Texture_Path).resize(self.TextureSize)
                if 'Glossiness' in str(refl_roughness_Texture_Path):
                    refl_roughness_Texture = ImageOps.invert(refl_roughness_Texture)
            except TypeError or IndexError:
                refl_roughness_Texture = Image.new('L',self.TextureSize,color = 255)

            try:
                refl_color_Texture_Path = refl_color_Texturelist[i]
                refl_color_Texture = Image.open(refl_color_Texture_Path).resize(self.TextureSize)
            except TypeError or IndexError:
                refl_color_Texture = Image.new('RGB',self.TextureSize,color = (255,255,255))
                ConvetBaseColor = False
                
            try:
                bump_input_Texture_Path = bump_input_Texturelist[i]
                bump_input_Texture = Image.open(bump_input_Texture_Path).resize(self.TextureSize)
            except TypeError or IndexError:
                bump_input_Texture = Image.new('RGB',self.TextureSize,color = (0,255,255))

            if MetallicPathList != None:
                # 如果存在金属度贴图
                MetallicPath = MetallicPathList[i]
                # 载入金属度贴图 
                MetallicTexture = Image.open(MetallicPath).resize(self.TextureSize)
            else:
                # 如果不存在金属度贴图
                ConvetBaseColor = False
                # 新建金属度贴图
                MetallicTexture = Image.new('L',self.TextureSize,color = 0)
            # 转换openGI为DirectX
            Normal_Texture = self.TransformNormal(bump_input_Texture)
            # 处理法线贴图路径
            Normal_texture_path = self.PathProcess(diffuse_color_Texturelist[i],'NormalN','.png')

            Normal_Texture.save(Normal_texture_path,'PNG')
            NewNormalPathList.append(Normal_texture_path)
            BaseColorTexture = self.MakeBaseColor(DiffuseTexture,refl_color_Texture,MetallicTexture)
            BaseColorPath = self.PathProcess(diffuse_color_Texturelist[i],'BaseColorN','.png')
            BaseColorTexture.save(BaseColorPath,'PNG')
            BaseColorPathList.append(BaseColorPath)
            ARMSTexture = self.MakeArmsTexture(refl_roughness_Texture,MetallicTexture)
            ARMSPath = self.PathProcess(diffuse_color_Texturelist[i],'ARMS','.png')
            if not os.path.exists(ARMSPath):
                ARMSTexture.save(ARMSPath,'PNG')
            ARMSPathList.append(ARMSPath)
        if ConvetBaseColor:
            self.TextureDict['diffuse_color'] = BaseColorPathList
        self.TextureDict['refl_roughness'] = ARMSPathList
        self.TextureDict['bump_input'] = NewNormalPathList
        return (self.TextureDict) 

    # 将RedshiftArchitecture转换为ARMS
    def ConvertATextureToARMS(self):
        # 判断给定的贴图列表的漫反射颜色是否不存在贴图，如果不存在就返回假
        if self.TextureDict['diffuse'] == None:
            return False
        TextureCount = len(self.TextureDict['diffuse'])

        refl_roughness_Texturelist     = self.TextureDict['refl_gloss']
        diffuse_color_Texturelist      = self.TextureDict['diffuse']
        refl_color_Texturelist         = self.TextureDict['refl_color']
        bump_input_Texturelist         = self.TextureDict['bump_input']
        refl_reflectivity_Texturelist  = self.TextureDict['brdf_0_degree_refl']
        if refl_reflectivity_Texturelist  != None:
            MetallicPathList = refl_reflectivity_Texturelist 
        else:
            MetallicPathList = None

        NewNormalPathList = []
        ARMSPathList = []
        BaseColorPathList = []
        ConvetBaseColor = True
        for i in range(0,TextureCount):
            DiffuseTexture = Image.open(diffuse_color_Texturelist[i]).resize(self.TextureSize)
            
            try:
                refl_roughness_Texture_Path = refl_roughness_Texturelist[i]
                refl_roughness_Texture = Image.open(refl_roughness_Texture_Path).resize(self.TextureSize)
                if 'Glossiness' in str(refl_roughness_Texture_Path):
                    refl_roughness_Texture = ImageOps.invert(refl_roughness_Texture)
            except TypeError or IndexError:
                refl_roughness_Texture = Image.new('L',self.TextureSize,color = 255)

            try:
                refl_color_Texture_Path = refl_color_Texturelist[i]
                refl_color_Texture = Image.open(refl_color_Texture_Path).resize(self.TextureSize)
            except TypeError or IndexError:
                refl_color_Texture = Image.new('RGB',self.TextureSize,color = (255,255,255))
                ConvetBaseColor = False
                
            try:
                bump_input_Texture_Path = bump_input_Texturelist[i]
                bump_input_Texture = Image.open(bump_input_Texture_Path).resize(self.TextureSize)
            except TypeError or IndexError:
                bump_input_Texture = Image.new('RGB',self.TextureSize,color = (0,255,255))

            if MetallicPathList != None:
                # 如果存在金属度贴图
                MetallicPath = MetallicPathList[i]
                # 载入金属度贴图 
                MetallicTexture = Image.open(MetallicPath).resize(self.TextureSize)
            else:
                # 如果不存在金属度贴图
                ConvetBaseColor = False
                # 新建金属度贴图
                MetallicTexture = Image.new('L',self.TextureSize,color = 0)
            # 转换openGI为DirectX
            Normal_Texture = self.TransformNormal(bump_input_Texture)
            # 处理法线贴图路径
            Normal_texture_path = self.PathProcess(diffuse_color_Texturelist[i],'NormalN','.png')

            Normal_Texture.save(Normal_texture_path,'PNG')
            NewNormalPathList.append(Normal_texture_path)
            BaseColorTexture = self.MakeBaseColor(DiffuseTexture,refl_color_Texture,MetallicTexture)
            BaseColorPath = self.PathProcess(diffuse_color_Texturelist[i],'BaseColorN','.png')
            BaseColorTexture.save(BaseColorPath,'PNG')
            BaseColorPathList.append(BaseColorPath)
            ARMSTexture = self.MakeArmsTexture(refl_roughness_Texture,MetallicTexture)
            ARMSPath = self.PathProcess(diffuse_color_Texturelist[i],'ARMS','.png')
            if not os.path.exists(ARMSPath):
                ARMSTexture.save(ARMSPath,'PNG')
            ARMSPathList.append(ARMSPath)
        if ConvetBaseColor:
            self.TextureDict['diffuse_color'] = BaseColorPathList
        else:
            self.TextureDict['diffuse_color'] = self.TextureDict['diffuse']
        self.TextureDict['refl_roughness'] = ARMSPathList
        self.TextureDict['bump_input'] = NewNormalPathList
        return (self.TextureDict) 

    def PathProcess(self,InputPath,Type,formate) -> str:
        import re
        pattern = re.compile(r'\.\d{4}\.')
        SearchResult = pattern.search(InputPath)
        if SearchResult == None:
            Newpath = "_".join(InputPath.split('_')[:-1]) + '_' + Type + formate
        else:
            Newpath = "_".join(InputPath.split('_')[:-1])  + '_' + Type + SearchResult.group() + formate
        Newpath = Newpath.replace('..','.')
        return(Newpath)

    def MakeArmsTexture(self,RoughnessTexture,MetallicTexture,AOTexture=None,ROUC=0,METC=0,AOC=0) -> Image:
        if AOTexture == None:
            R = Image.new('L',self.TextureSize,color = 255)
        else:
            R = (AOTexture.split())[AOC]
        G = (RoughnessTexture.split())[ROUC]
        B = (MetallicTexture.split())[METC]
        A = Image.new('L',self.TextureSize,color = 255)
        ARMSTexture = Image.merge('RGBA',[R,G,B,A])
        return ARMSTexture

    def MakeBaseColor(self,DiffuseTexture,ReflectionTexture,MetaiilcTexture):
        MetaiilcTexture = MetaiilcTexture.split()[0]
        BaseColorTexture = Image.composite(ReflectionTexture,DiffuseTexture,MetaiilcTexture)
        return BaseColorTexture

    def TransformNormal(self,NormalMap):
        r = NormalMap.split()[0]
        g = NormalMap.split()[1]
        b = NormalMap.split()[2]
        g = ImageOps.invert(g)
        a = Image.new('L',NormalMap.size,color = 255)
        newNormalTexture = Image.merge('RGBA',[r,g,b,a])
        return newNormalTexture
    @staticmethod
    def resizeTexture(TexturePath):
        Img = Image.open(TexturePath).resize((2048,2048))
        try:
            Img.save(TexturePath)
        except PermissionError:
            os.chmod( TexturePath, os.stat.S_IWRITE )
            Img.save(TexturePath)
    @staticmethod
    def resizerTextures(TexturePathList):
        for TexturePath in TexturePathList:
            ConvertTexture.resizeTexture(TexturePath)
#functions
def analyseJson(jsondata):
        materialinfoDictList = []
        #遍历所有材质球
        for key in jsondata.keys():
            materialinfoDict = {
                'Materialname'   : None,
                'Type'           : 'ARMS',
                'CreateMaterial' : True,
                'TexturePath'    : {},
                'UseForChar'     : False,
                'HasTex'         : False,
            }
            MTexturePath = {
                'refl_roughness'    :  None,
                'diffuse_color'     :  None,
                'refl_reflectivity' :  None,
                'refl_color'        :  None,
                'bump_input'        :  None,
                'emission_color'    :  None,
                'refl_metalness'    :  None,
                'refl_aniso'        :  None,
                'coat_color'        :  None,
                'coat_weight'       :  None,
                'opacity_color'     :  None,
            }
            ATexturepath = {
                'brdf_0_degree_refl'    : None,
                'bump_input'            : None,
                'refl_color'            : None,
                'refl_gloss'            : None,
                'diffuse'               : None,
                'emission_color'        :  None,
            }
            #获取材质球名称
            value = jsondata[key]
            materialnmae = key.split(';')[0]
            materialType = key.split(';')[1]
            #判断贴图路径是否为空
            if value == {}:
                #不包含贴图
                materialinfoDict['CreateMaterial'] = False
            #判断是否是RSM材质球
            if materialType == 'RedshiftMaterial':
                materialinfoDict['TexturePath'] = MTexturePath
                for TextureTpye in value.keys():
                    if TextureTpye in MTexturePath.keys():
                        MTexturePath[TextureTpye] = [elem for elem in value[TextureTpye].values()][0]
                keyWords = ['kouqiang','yanqiu','boliti','jiemao','YanJian','skin']
                for keyWord in keyWords:
                    if keyWord in materialnmae.lower():
                        materialinfoDict['UseForChar'] = True
                        break
                #如果不是ARMS贴图
                if 'ARMS' not in str(value) and not materialinfoDict['UseForChar']:
                    NewinfoOb = ConvertTexture(materialinfoDict['TexturePath'],2048)
                    Newinfo = NewinfoOb.ConvertMTextureToARMS()
                    if Newinfo != False :
                        materialinfoDict['TexturePath'] = Newinfo
                    else:
                        materialinfoDict['CreateMaterial'] = False
                elif materialinfoDict['UseForChar']:
                    pass
                else:
                    pass
            elif materialType == 'RedshiftArchitectural':
                materialinfoDict['TexturePath'] = ATexturepath
                for TextureTpye in value.keys():
                    if TextureTpye in ATexturepath.keys():
                        ATexturepath[TextureTpye] = [elem for elem in value[TextureTpye].values()][0]
                NewinfoOb = ConvertTexture(materialinfoDict['TexturePath'],2048)
                Newinfo = NewinfoOb.ConvertATextureToARMS()
                if Newinfo != False :
                    materialinfoDict['TexturePath'] = Newinfo
                else:
                    materialinfoDict['CreateMaterial'] = False

            else:
                # 不是rs材质球
                materialinfoDict['CreateMaterial'] = False
            materialinfoDict['Materialname'] = materialnmae
            materialinfoDictList.append(materialinfoDict)
        return materialinfoDictList
def ReadJsonFile(fileName):
    file = open(fileName,'r')
    data = json.loads(file.read())
    file.close()
    return(data)
def calcMD5(text):
    import hashlib
    m = hashlib.md5()
    m.update(text.encode('utf-8'))
    return(m.hexdigest())
def NormalizePath(path:str) -> str:
    path = os.path.normpath(path)
    return(path.replace('\\','/'))
def ConvertSizeToStr(size):
    unittype = ["KB","MB","GB"]
    reslut = ""
    for unit in unittype:
        size = size/1024
        if size < 1024:
            reslut =f"{round(size,2)} {unit}"
            return reslut
def getfilesFromPath(path,extension=None):
    filePaths = []
    for root,folder,files in os.walk(path):
        if extension !=  None:
            extension = extension.lower()
            files = [file for file in files if file.casefold().endswith(extension)]
        for file in files:
            filePaths.append(os.path.join(root,file))
    return filePaths
def applyMacro(parten,parseresult):
    for key in parseresult:
        parten = parten.replace(f"${key}",parseresult[key])
    return parten
def getFilesDataFrompath(path,extension=None):
    files = getfilesFromPath(path,extension)
    Datas = []
    for file in files:
        modifyTime = str(time.asctime(time.localtime(os.path.getmtime(file))))
        size = os.path.getsize(file)
        path = file
        name = os.path.splitext(os.path.basename(file))[0]
        md5 = calcMD5(name + modifyTime + path)
        dicData = {}
        dicData["name"] = name
        dicData["modifyTime"] = modifyTime
        dicData["size"] = ConvertSizeToStr(size)
        dicData["path"] = path
        dicData["MD5"] = md5
        dicData["imported"] = False
        Datas.append(dicData)
    return Datas
def parseCameraName(name):
    parseResult = {}
    nameSlpitList = name.split("_")
    if len(nameSlpitList) < 5:
        return False # 如果名称不合法返回假
    parseResult["ep"] = name.split("_")[0]
    parseResult["sc"] = name.split("_")[1]
    parseResult["number"] = name.split("_")[2]
    parseResult["frameStart"] = name.split("_")[3]
    parseResult["frameEnd"] = name.split("_")[4]
    parseResult["fullName"] = name.split(".")[0]
    return parseResult
def isPathValid(path):
    if not os.path.isdir(path):
        return False
    if not os.path.exists(path):
        return False
    return True


def importAssetByJsonPath(jsonPath:str):
    with open(jsonPath,'r',encoding='utf-8') as f:
        assetData = json.loads(f.read())
    
def parseStaticMeshName(name,sceneName):
    parseResult = {}
    parseResult["name"] = name
    if sceneName:
        parseResult["scenename"] = sceneName
    else:
        parseResult["scenename"] = ""
    return parseResult

def generate_random_string(length=10):
    # 定义生成随机字符串的字符集
    characters = string.ascii_letters + string.digits
    # 使用 random.choices 从字符集中随机选择字符，形成指定长度的字符串
    random_string = ''.join(random.choices(characters, k=length))
    return random_string
def generate_unique_string(length=10):
    while(1):
        random_string = generate_random_string(length)
        if Backend.Get().getAsset(random_string) == False:
            return random_string

def copy_folder(src:str,des:str):
    shutil.copytree(src,des)


def CopyFileToFolder(filePath:str,folder:str,newName:str = None,move:bool=False):
    if not os.path.exists(filePath):
        return ""
    newFileName = os.path.basename(filePath)
    if newName:
        newFileName = newName
    newFilePath = os.path.join(folder,newFileName)
    if move:
        shutil.move(filePath,newFilePath)
    else:
        shutil.copyfile(filePath,newFilePath)
    return os.path.basename(newFilePath)

if __name__ == "__main__":
    from UnrealPipeline import reloadModule
    reloadModule()