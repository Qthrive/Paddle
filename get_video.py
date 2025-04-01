import requests
import re
import json

# 这个备选
url = 'https://www.bilibili.com/video/BV1cu411G7Km/?spm_id_from=333.337.search-card.all.click&vd_source=dbaeaef5a27c53bb0d3d240896fb9c43'

headers = {
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36',
    'Cookie':"_uuid=972E41510-C15B-38A2-D1C9-869ED85510E7791793infoc; buvid_fp=e1016ec9b56272437d3138fd3dc1c003; buvid3=578F14BC-CCBB-4A4A-DEBB-E25E4702E2F492973infoc; b_nut=1739662993; buvid4=D74E90CD-3263-B051-948E-8965ABF2670292973-025021523-KX9XcNa58kdmJcmKOVEf8A%3D%3D; header_theme_version=CLOSE; enable_web_push=DISABLE; rpdid=|(umJmYJm~|u0J'u~JmY~RmY~; hit-dyn-v2=1; DedeUserID=441083700; DedeUserID__ckMd5=159fc71ceaf10289; LIVE_BUVID=AUTO5517401464584334; CURRENT_QUALITY=120; enable_feed_channel=ENABLE; home_feed_column=5; bili_ticket=eyJhbGciOiJIUzI1NiIsImtpZCI6InMwMyIsInR5cCI6IkpXVCJ9.eyJleHAiOjE3NDMzMjc4MzMsImlhdCI6MTc0MzA2ODU3MywicGx0IjotMX0.7Itxc3h9ZtZ85xK-OJBzyPjS6l73DE5WaEDpc8ADfUk; bili_ticket_expires=1743327773; SESSDATA=d24934d0%2C1758620633%2C3c8ba%2A31CjDrLFqAGgOKWNcRvIpZt0PaLHnL_HAkhWNYqvIe_y0idot6yKE4N6rVIqeMjRAahrYSVmdNMlBiV25feE0zTnpzM2p0SVp6c0VRNF9RTS0wYXpqTzEtc1psSUtOMWV6OVBBUk5LODNkd0ppUU92dTBKYkZ0cFp3RHhIZVVJVWpqVVZENEVJcm93IIEC; bili_jct=a63cc5c8ffc8e2793a9e266ce0d80033; sid=4up3zfix; PVID=3; bp_t_offset_441083700=1049610245304745984; b_lsid=510105A10FA_195E14A07A7; browser_resolution=1707-791; bmg_af_switch=1; bmg_src_def_domain=i0.hdslb.com; bsource=search_google; CURRENT_FNVAL=4048",
    #备选 'Referer':"https://search.bilibili.com/all?keyword=%E6%9C%B1%E4%B8%96%E8%B5%AB&from_source=webtop_search&spm_id_from=333.1007&search_source=3"
    'Referer':"https://search.bilibili.com/all?keyword=%E6%9C%B1%E4%B8%96%E8%B5%AB&from_source=webtop_search&spm_id_from=333.1007&search_source=3"
}

response = requests.get(url=url,headers=headers).text
# with open(r'./codes/res.txt','w',encoding='utf-8') as f:
#     f.write(response)
# print(response)
data_str = re.findall(r'window.__playinfo__=(.*?)</script><script>window.__INITIAL_STATE',response)[0]
data = json.loads(data_str)
# for video_url in data:
#     video_response = requests.get(url=video_url,headers=headers,stream=True).content
#     with open(r'./codes/video.mp4','ab') as f:
#         f.write(video_response)
# with open(r'./codes/data.json','w',encoding='utf-8') as f:
#     json.dump(data,f,ensure_ascii=False,indent=4)
high_data = data['data']['dash']['video'][0]
links = re.findall(r'"id":116,"baseUrl":"(.*?)",',data_str)
# links = re.findall(r'"id":64,"baseUrl":"(.*?)",',data_str)
for video_url in links:
    video_response = requests.get(url=video_url,headers=headers,stream=True).content
    with open(r'./codes/video.mp4','ab') as f:
        f.write(video_response)