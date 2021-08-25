# Bilibili api for Tencent Cloud Function

## 概述

参考项目 [github.com/aolose/bilibili-api-function](https://github.com/aolose/bilibili-api-function) 给出 `python` 的实现.

插件 `解除b站区域限制` 中同代理服务器相关的代码在3889行的 `const playurl = ...` 中:

```javascript
const playurl = new BilibiliApi({
    asyncAjax: function (originUrl) {
        ui.playerMsg(`从${r.const.server.CUSTOM === balh_config.server_inner ? '自定义' : '代理'}服务器拉取视频地址中...`);
        return (r.const.server.CUSTOM === balh_config.server_inner ? playurl_by_custom._asyncAjax(originUrl) : (playurl_by_proxy._asyncAjax(originUrl) // 优先从代理服务器获取
            .catch(e => {
                if (e instanceof AjaxException) {
                    ui.playerMsg(e);
                    if (e.code === 1 // code: 1 表示非番剧视频, 不能使用番剧视频参数
                        || (Strings.getSearchParam(originUrl, 'module') === 'bangumi' && e.code === -404)) { // 某些番剧视频又不需要加module=bangumi, 详见: https://github.com/ipcjs/bilibili-helper/issues/494
                        ui.playerMsg('尝试使用非番剧视频接口拉取视频地址...');
                        return playurl_by_proxy._asyncAjax(originUrl, false)
                            .catch(e2 => Promise$1.reject(e)) // 忽略e2, 返回原始错误e
                    } else if (e.code === 10004) { // code: 10004, 表示视频被隐藏, 一般添加module=bangumi参数可以拉取到视频
                        ui.playerMsg('尝试使用番剧视频接口拉取视频地址...');
                        return playurl_by_proxy._asyncAjax(originUrl, true)
                            .catch(e2 => Promise$1.reject(e))
                    }
                }
                return Promise$1.reject(e)
            })))
```

其中 originUrl 可能为 "//api.bilibili.com/pgc/player/web/playurl?avid=584789567&cid=250248984&qn=80&fnver=0&fnval=80&fourk=1&ep_id=341099&session=c5b545b8198808c9d597db08f58212bd&module=bangumi" 用于请求番剧视频地址.

使用首选代理服务器部分涉及到的代码为 (其中变量 `balh_config.server_custom` 正是填入设置中的自定义(首选服务器)的地址.):

```javascript
// 请求解析 originUrl 的主体
const playurl_by_custom = new BilibiliApi({
    _asyncAjax: function (originUrl) {
        return this.selectServer(originUrl).then(r => this.processProxySuccess(r))
    },
    // selectServer 的定义
    selectServer: async function (originUrl) {
        let result;
        // 对应this.transToProxyUrl的参数, 用`/`分隔, 形如: `${proxyHost}/${area}`
        let tried_server_args = [];
        const isTriedServerArg = (proxyHost, area) => tried_server_args.includes(`${proxyHost}/*`) || tried_server_args.includes(`${proxyHost}/${area}`);

        // 重要函数, 涉及到对代理服务器的请求方式
        const requestPlayUrl = (proxyHost, area = '') => {
            tried_server_args.push(`${proxyHost}/${area}`);
            return Async.ajax(this.transToProxyUrl(originUrl, proxyHost, area))
                // 捕获错误, 防止依次尝试各各服务器的流程中止
                .catch((e) => {
                    // proxyHost临时不可用, 将它添加到tried_server_args中, 防止重复请求
                    tried_server_args.push(`${proxyHost}/*`);
                    return ({ code: -1, error: e });
                })
        };
        // ...
        // 首选服务器解析
        if (balh_config.server_custom) {
            ui.playerMsg('使用首选代理服务器拉取视频地址...');
            result = await requestPlayUrl(balh_config.server_custom);
            if (!result.code) {
                // Promise$1 是备份的 window.Promise
                return Promise$1.resolve(result)
            }
        }
    },
    // transToProxyUrl 的定义
    // 它会返回
    // https://service-ivf5n4nf-1307133634.sh.apigw.tencentcs.com/release/playurl?avid=584789567&cid=250248984&qn=80&fnver=0&fnval=80&fourk=1&ep_id=341099&session=a2e5fe2ebaee763d5c201db16e73cf04&module=bangumi&access_key=e9299b6ec777433caa73717f888d9281
    transToProxyUrl: function (originUrl, proxyHost, area = '') {
        if (r.regex.bilibili_api_proxy.test(proxyHost)) {
            if (area === 'th') {
                // 泰区番剧解析
                return getMobiPlayUrl(originUrl, proxyHost, true)
            }
            if (window.__balh_app_only__) {
                // APP 限定用 mobi api
                return getMobiPlayUrl(originUrl, proxyHost)
            }
            return originUrl.replace(/^(https:)?(\/\/api\.bilibili\.com\/)/, `$1${proxyHost}/`) + '&area=' + area + access_key_param_if_exist(true);
        } else {
            if (window.__balh_app_only__) {
                return `${proxyHost}?${generateMobiPlayUrlParams(originUrl)}`
            }
            // 将proxyHost当成接口的完整路径进行拼接
            const params = originUrl.split('?')[1];
            return `${proxyHost}?${params}${access_key_param_if_exist(true)}`

        }
    },
    // ...
})
```

因此我们要做的就是为服务器 (或者云函数) 实现正确返回 `result` 的功能. 