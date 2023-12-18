from bs4 import BeautifulSoup
import requests 
import base64
from urllib.parse import unquote
import re
class VidSrcEx:

    def getFutoken(self,key,url) ->str :
        req = requests.get('https://vidplay.site/futoken',{'Referer': url})
        fu_key = re.search(r"var\s+k\s*=\s*'([^']+)'", req.text).group(1)
        # print(fu_key)
        # print(f"{fu_key},{','.join([str(ord(fu_key[i % len(fu_key)]) + ord(key[i])) for i in range(len(key))])}"

        return f"{fu_key},{','.join([str(ord(fu_key[i % len(fu_key)]) + ord(key[i])) for i in range(len(key))])}"

        

    def keyPermution(self,key,data) -> str:
        state = list(range(256))
        index1 = 0

        for i in range(256):
            index1 = ((index1 + state[i]) + ord(key[i % len(key)])) % 256
            state[i], state[index1] = state[index1], state[i]

        index1 = index2 = 0
        finalKey = ''

        for char in range(len(data)):
            index1 = (index1 + 1) % 256
            index2 = (index2 + state[index1]) % 256
            state[index1], state[index2] = state[index2], state[index1]

            if isinstance(data[char], str):
                finalKey += chr(ord(data[char]) ^ state[(state[index1] + state[index2]) % 256])
            elif isinstance(data[char], int):
                finalKey += chr((data[char]) ^ state[(state[index1] + state[index2]) % 256])
        # print(finalKey)
        return finalKey


    def encodeId(self,vId) -> str:
        key1 , key2 = requests.get('https://raw.githubusercontent.com/Claudemirovsky/worstsource-keys/keys/keys.json').json()
        decodeId = self.keyPermution(key1,vId).encode('Latin_1')
        encodedResult = self.keyPermution(key2,decodeId).encode('latin_1')
        encodeBase64 = base64.b64encode(encodedResult)
        return encodeBase64.decode('utf-8').replace('/','_')
    def handleVidplay(self,url) -> str:
        key = self.encodeId(url.split('/e/')[1].split('?')[0])
        data = self.getFutoken(key , url)
        req = requests.get(f"https://vidplay.site/mediainfo/{data}?{url.split('?')[1]}&autostart=true", headers={"Referer": url})
        try:
            m3u8Data = req.json()['result']['sources'][0]['file']
            return m3u8Data
        except Exception as err :
            return(None)
    def decode(self,str)->bytearray:
        keyBytes = bytes('8z5Ag5wgagfsOuhz', 'utf-8')
        j = 0
        s = bytearray(range(256))
        
        for i in range (256):
            j = (j+s[i] + keyBytes[i%len(keyBytes)]) & 0xff
            s[i],s[j] = s[j],s[i]
        decoded = bytearray(len(str))
        i = 0
        k = 0 
        for index in range(len(str)):
            i = (i+1) & 0xff
            k = (k+ s[i]) & 0xff
            s[i],s[k]=s[k],s[i]
            t =(s[i] +s[k]) & 0xff
            decoded[index] = str[index] ^ s[t]

        # print(decoded)
        return decoded 

    def decodeBase64UrlSafe(self,sourceUrl):
        standardizedInput = sourceUrl.replace('_','/').replace('-','+')
        binaryData=base64.b64decode(standardizedInput)
        return bytearray(binaryData)

    def decryptSourceUrl(self,sourceUrl)->str:
        encoded = self.decodeBase64UrlSafe(sourceUrl)
        decoded = self.decode(encoded)
        decoded_text = decoded.decode('utf-8')
        return unquote(decoded_text)

    def getSourceUrl(self,source_id) -> str:
        req = requests.get(f'https://vidsrc.to/ajax/embed/source/{source_id}')
        data = req.json()
        encryptedSourceUrl = data['result']['url']
        return self.decryptSourceUrl(encryptedSourceUrl)

    def get_sources(self,data_id):
        objSrc = {}
        req = requests.get(f'https://vidsrc.to/ajax/embed/episode/{data_id}/sources')
        data = req.json()['result']
        
        for obj in data:
            objSrc[obj['title']] = obj['id']
        
        return objSrc
        # print({video.get('title'):video.get('id') for video in data.get('result')})

    def main(self,source_name, imdb ):
        req = requests.get(f'https://vidsrc.to/embed/movie/{imdb}')
        soup = BeautifulSoup(req.text,'html.parser')
        source_code = soup.find('a',{'data-id':True}).get('data-id')
        sources = self.get_sources(source_code)
        source = sources.get(source_name)
        if not source :
            print(f'no source found for {source_name}')
        source_url = self.getSourceUrl(source)
        # print(source_url)
        if 'vidplay' in source_url:
            return self.handleVidplay(source_url)
if __name__ == '__main__':
    vid = VidSrcEx()
    video = vid.main("Vidplay",'299534')
    print(video)