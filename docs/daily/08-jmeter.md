# 阶段八：先让请求正确，再解释负载结果

[每日目录](README.md) · [上一阶段](07-ci.md) · [下一阶段](09-delivery.md) · [JMeter 讲解](../JMETER.md) · [练习 07](../../exercises/exercise_07_jmeter.md)

本章默认 Windows PowerShell；Java/JMeter 是额外工具，不会由 pip 安装。Linux 等价命令见 [JMeter 讲解](../JMETER.md)。服务与 JMeter 在同一系统运行，目标保持本机 127.0.0.1。本周写 `docs/jmeter_practice.md` 和 `performance/my_report.md`，大文件放 reports 并另行留存。没有真实执行就不填结果数字。

<a id="day-1"></a>

## 第 1 天：准备 Java/JMeter 与专用靶场

**材料：** JMeter 讲解第 1 节，[Apache 下载页](https://jmeter.apache.org/download_jmeter.cgi)。

**操作：**

1. 准备兼容的 Java 与 Apache JMeter；教程计划基于 JMeter 5.6.3、示例 Java 17，下载版本不同时记录实际版本并验证兼容性。
2. 在 PowerShell 设置实际安装路径，执行版本命令（示例路径不存在时先改，不原样照抄）：

```powershell
$lessonJmeter = 'D:\tools\apache-jmeter-5.6.3\bin\jmeter.bat'
java -version
& $lessonJmeter -v
```

3. 终端 A 启动专用服务；确认其他手动服务没有占用 8765。终端 B 检查 health：

```powershell
# 终端 A
.\.venv\Scripts\python.exe -m sandbox.task_api --port 8765 --db reports/learning/jmeter-only.sqlite3
```

```powershell
# 终端 B
(Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8765/health).StatusCode
```

4. 记录机器/OS/Python/Java/JMeter、代码版本与本地差异、数据库路径和初始任务数。后续每个新 B 终端需重新设置 `$lessonJmeter`。




<!-- daily-reference:start -->
**当天写完后的参考代码：**

先按原步骤在终端A启动专用服务；在终端B运行本脚本，-Jmeter传自己的安装路径。脚本只检查已安装工具，不自动下载，也不声称版本输出代表负载成功。

文件 `exercises/jmeter/day01_environment.ps1` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/08/day01/exercises/jmeter/day01_environment.ps1)

```powershell
param([string]$Jmeter = 'D:\tools\apache-jmeter-5.6.3\bin\jmeter.bat')
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Jmeter)) { throw '请用-Jmeter参数传入实际jmeter.bat路径' }
java -version
if ($LASTEXITCODE -ne 0) { throw 'Java不可用' }
& $Jmeter -v
if ($LASTEXITCODE -ne 0) { throw 'JMeter不可用' }
$lessonHealth = Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8765/health
if ($lessonHealth.StatusCode -ne 200) { throw '靶场未就绪' }
Write-Output 'Java/JMeter可用，靶场health=200；记录真实版本。'
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
& .\exercises\jmeter\day01_environment.ps1
```

**对照运行后的结果：** Java与JMeter版本可读，health200，退出0。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 真实版本输出和 health 200，确认是专用数据库。
- [ ] 能说明 pytest fixture 服务不能拿来作为手动 JMeter 的固定服务。
- [ ] 工具缺失或 health 不通时停在准备阶段，不开始加线程。

**卡住时：** 命令找不到 Java 检查安装与 PATH；连接拒绝核对终端 A，而不是加大线程数重试。

<a id="day-2"></a>

## 第 2 天：在 GUI 中读懂 token/ID 关联

**材料：** `performance/task_workflow.jmx` 与 JMeter 讲解第 2 节。

**操作：**

1. 将原计划复制为自己的练习文件，再打开 GUI：

```powershell
Copy-Item performance/task_workflow.jmx performance/my_task_workflow.jmx
& $lessonJmeter -t performance/my_task_workflow.jmx
```

已有自己的文件时先保留，不重复覆盖。GUI 中展开 `Task users → Login once per thread → 01_login`，找到 `Extract thread token` 的 `$.token` → `auth_token`。

2. 展开 `Task business workflow → 02_create`，找到 `$.id` → `task_id`；查后续 URL 中 `${task_id}` 与 Header 中 `${auth_token}`。
3. 找 `05_verify_update` 的 Groovy 断言，解释为什么除了状态码还要检查当前 ID 和 status=done；检查 `07_verify_deleted` 期望 404 并假定成功后再断言。
4. 临时添加“查看结果树”，以默认 1 线程×3 轮运行，查看每步是否成功；结束后禁用或移除该监听器再保存。GUI 中显示的 token/响应不复制进报告。




<!-- daily-reference:start -->
**当天写完后的参考代码：**

上面是完整计划文件，不需要凭描述自己拼XML。GUI中定位每线程登录、token/ID提取与每轮六个业务请求；调试结果树只临时启用，保存用于负载的计划前关闭。

文件 `performance/my_task_workflow.jmx` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/08/day02/performance/my_task_workflow.jmx)

完整JMX；可直接保存后用GUI打开。已有自己修改的文件时先对照，不覆盖个人成果。

```xml
<?xml version='1.0' encoding='UTF-8'?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="Local task API workflow" enabled="true">
      <stringProp name="TestPlan.comments">Local training only. Default: 1 thread, 3 loops, 19 samples. Stop thread on failure.</stringProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
        <collectionProp name="Arguments.arguments" />
      </elementProp>
    </TestPlan>
    <hashTree>
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Task users" enabled="true">
        <stringProp name="ThreadGroup.on_sample_error">stopthread</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="Loop Controller" enabled="true">
          <boolProp name="LoopController.continue_forever">false</boolProp>
          <stringProp name="LoopController.loops">${__P(loops,3)}</stringProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">${__P(threads,1)}</stringProp>
        <stringProp name="ThreadGroup.ramp_time">${__P(ramp_up,1)}</stringProp>
        <stringProp name="ThreadGroup.duration" />
        <stringProp name="ThreadGroup.delay" />
        <boolProp name="ThreadGroup.scheduler">false</boolProp>
        <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
      </ThreadGroup>
      <hashTree>
        <ConfigTestElement guiclass="HttpDefaultsGui" testclass="ConfigTestElement" testname="HTTP defaults" enabled="true">
          <stringProp name="HTTPSampler.domain">${__P(host,127.0.0.1)}</stringProp>
          <stringProp name="HTTPSampler.port">${__P(port,8765)}</stringProp>
          <stringProp name="HTTPSampler.protocol">http</stringProp>
          <stringProp name="HTTPSampler.contentEncoding">UTF-8</stringProp>
          <stringProp name="HTTPSampler.connect_timeout">3000</stringProp>
          <stringProp name="HTTPSampler.response_timeout">5000</stringProp>
          <stringProp name="HTTPSampler.implementation">HttpClient4</stringProp>
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
            <collectionProp name="Arguments.arguments" />
          </elementProp>
        </ConfigTestElement>
        <hashTree />
        <HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="JSON headers" enabled="true">
          <collectionProp name="HeaderManager.headers">
            <elementProp name="" elementType="Header">
              <stringProp name="Header.name">Content-Type</stringProp>
              <stringProp name="Header.value">application/json</stringProp>
            </elementProp>
          </collectionProp>
        </HeaderManager>
        <hashTree />
        <OnceOnlyController guiclass="OnceOnlyControllerGui" testclass="OnceOnlyController" testname="Login once per thread" enabled="true" />
        <hashTree>
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="01_login" enabled="true">
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
              <collectionProp name="Arguments.arguments">
                <elementProp name="" elementType="HTTPArgument">
                  <boolProp name="HTTPArgument.always_encode">false</boolProp>
                  <stringProp name="Argument.value">{"username":"alice","password":"alice-pass"}</stringProp>
                  <stringProp name="Argument.metadata">=</stringProp>
                </elementProp>
              </collectionProp>
            </elementProp>
            <boolProp name="HTTPSampler.postBodyRaw">true</boolProp>
            <stringProp name="HTTPSampler.path">/login</stringProp>
            <stringProp name="HTTPSampler.method">POST</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">false</boolProp>
            <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          </HTTPSamplerProxy>
          <hashTree>
            <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Expect HTTP 200" enabled="true">
              <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
              <boolProp name="Assertion.assume_success">true</boolProp>
              <intProp name="Assertion.test_type">8</intProp>
              <collectionProp name="Asserion.test_strings">
                <stringProp name="0">200</stringProp>
              </collectionProp>
            </ResponseAssertion>
            <hashTree />
            <JSONPostProcessor guiclass="JSONPostProcessorGui" testclass="JSONPostProcessor" testname="Extract thread token" enabled="true">
              <stringProp name="JSONPostProcessor.referenceNames">auth_token</stringProp>
              <stringProp name="JSONPostProcessor.jsonPathExprs">$.token</stringProp>
              <stringProp name="JSONPostProcessor.match_numbers">1</stringProp>
              <stringProp name="JSONPostProcessor.defaultValues">MISSING</stringProp>
              <boolProp name="JSONPostProcessor.compute_concat">false</boolProp>
            </JSONPostProcessor>
            <hashTree />
          </hashTree>
        </hashTree>
        <GenericController guiclass="LogicControllerGui" testclass="GenericController" testname="Task business workflow" enabled="true" />
        <hashTree>
          <HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="Bearer token" enabled="true">
            <collectionProp name="HeaderManager.headers">
              <elementProp name="" elementType="Header">
                <stringProp name="Header.name">Authorization</stringProp>
                <stringProp name="Header.value">Bearer ${auth_token}</stringProp>
              </elementProp>
            </collectionProp>
          </HeaderManager>
          <hashTree />
          <ConstantTimer guiclass="ConstantTimerGui" testclass="ConstantTimer" testname="Think time before each business request" enabled="true">
            <stringProp name="ConstantTimer.delay">${__P(think_ms,200)}</stringProp>
          </ConstantTimer>
          <hashTree />
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="02_create" enabled="true">
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
              <collectionProp name="Arguments.arguments">
                <elementProp name="" elementType="HTTPArgument">
                  <boolProp name="HTTPArgument.always_encode">false</boolProp>
                  <stringProp name="Argument.value">{"title":"jm-${__P(run_id,local)}-${__threadNum}-${__counter(FALSE,)}"}</stringProp>
                  <stringProp name="Argument.metadata">=</stringProp>
                </elementProp>
              </collectionProp>
            </elementProp>
            <boolProp name="HTTPSampler.postBodyRaw">true</boolProp>
            <stringProp name="HTTPSampler.path">/tasks</stringProp>
            <stringProp name="HTTPSampler.method">POST</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">false</boolProp>
            <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          </HTTPSamplerProxy>
          <hashTree>
            <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Expect HTTP 201" enabled="true">
              <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
              <boolProp name="Assertion.assume_success">true</boolProp>
              <intProp name="Assertion.test_type">8</intProp>
              <collectionProp name="Asserion.test_strings">
                <stringProp name="0">201</stringProp>
              </collectionProp>
            </ResponseAssertion>
            <hashTree />
            <JSONPostProcessor guiclass="JSONPostProcessorGui" testclass="JSONPostProcessor" testname="Extract task ID" enabled="true">
              <stringProp name="JSONPostProcessor.referenceNames">task_id</stringProp>
              <stringProp name="JSONPostProcessor.jsonPathExprs">$.id</stringProp>
              <stringProp name="JSONPostProcessor.match_numbers">1</stringProp>
              <stringProp name="JSONPostProcessor.defaultValues">MISSING</stringProp>
              <boolProp name="JSONPostProcessor.compute_concat">false</boolProp>
            </JSONPostProcessor>
            <hashTree />
          </hashTree>
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="03_read" enabled="true">
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
              <collectionProp name="Arguments.arguments" />
            </elementProp>
            <stringProp name="HTTPSampler.path">/tasks/${task_id}</stringProp>
            <stringProp name="HTTPSampler.method">GET</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">false</boolProp>
            <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          </HTTPSamplerProxy>
          <hashTree>
            <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Expect HTTP 200" enabled="true">
              <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
              <boolProp name="Assertion.assume_success">true</boolProp>
              <intProp name="Assertion.test_type">8</intProp>
              <collectionProp name="Asserion.test_strings">
                <stringProp name="0">200</stringProp>
              </collectionProp>
            </ResponseAssertion>
            <hashTree />
          </hashTree>
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="04_update" enabled="true">
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
              <collectionProp name="Arguments.arguments">
                <elementProp name="" elementType="HTTPArgument">
                  <boolProp name="HTTPArgument.always_encode">false</boolProp>
                  <stringProp name="Argument.value">{"status":"done"}</stringProp>
                  <stringProp name="Argument.metadata">=</stringProp>
                </elementProp>
              </collectionProp>
            </elementProp>
            <boolProp name="HTTPSampler.postBodyRaw">true</boolProp>
            <stringProp name="HTTPSampler.path">/tasks/${task_id}</stringProp>
            <stringProp name="HTTPSampler.method">PUT</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">false</boolProp>
            <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          </HTTPSamplerProxy>
          <hashTree>
            <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Expect HTTP 200" enabled="true">
              <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
              <boolProp name="Assertion.assume_success">true</boolProp>
              <intProp name="Assertion.test_type">8</intProp>
              <collectionProp name="Asserion.test_strings">
                <stringProp name="0">200</stringProp>
              </collectionProp>
            </ResponseAssertion>
            <hashTree />
          </hashTree>
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="05_verify_update" enabled="true">
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
              <collectionProp name="Arguments.arguments" />
            </elementProp>
            <stringProp name="HTTPSampler.path">/tasks/${task_id}</stringProp>
            <stringProp name="HTTPSampler.method">GET</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">false</boolProp>
            <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          </HTTPSamplerProxy>
          <hashTree>
            <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Expect HTTP 200" enabled="true">
              <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
              <boolProp name="Assertion.assume_success">true</boolProp>
              <intProp name="Assertion.test_type">8</intProp>
              <collectionProp name="Asserion.test_strings">
                <stringProp name="0">200</stringProp>
              </collectionProp>
            </ResponseAssertion>
            <hashTree />
            <JSR223Assertion guiclass="TestBeanGUI" testclass="JSR223Assertion" testname="Persisted task must be done" enabled="true">
              <stringProp name="scriptLanguage">groovy</stringProp>
              <stringProp name="parameters" />
              <stringProp name="filename" />
              <stringProp name="cacheKey">true</stringProp>
              <stringProp name="script">def task = new groovy.json.JsonSlurper().parseText(prev.getResponseDataAsString())
if (task.status != 'done' || task.id.toString() != vars.get('task_id')) {
    AssertionResult.setFailure(true)
    AssertionResult.setFailureMessage('Expected current task ID and persisted status=done')
}
</stringProp>
            </JSR223Assertion>
            <hashTree />
          </hashTree>
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="06_delete" enabled="true">
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
              <collectionProp name="Arguments.arguments" />
            </elementProp>
            <stringProp name="HTTPSampler.path">/tasks/${task_id}</stringProp>
            <stringProp name="HTTPSampler.method">DELETE</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">false</boolProp>
            <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          </HTTPSamplerProxy>
          <hashTree>
            <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Expect HTTP 204" enabled="true">
              <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
              <boolProp name="Assertion.assume_success">true</boolProp>
              <intProp name="Assertion.test_type">8</intProp>
              <collectionProp name="Asserion.test_strings">
                <stringProp name="0">204</stringProp>
              </collectionProp>
            </ResponseAssertion>
            <hashTree />
          </hashTree>
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="07_verify_deleted" enabled="true">
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
              <collectionProp name="Arguments.arguments" />
            </elementProp>
            <stringProp name="HTTPSampler.path">/tasks/${task_id}</stringProp>
            <stringProp name="HTTPSampler.method">GET</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">false</boolProp>
            <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          </HTTPSamplerProxy>
          <hashTree>
            <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Expect HTTP 404" enabled="true">
              <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
              <boolProp name="Assertion.assume_success">true</boolProp>
              <intProp name="Assertion.test_type">8</intProp>
              <collectionProp name="Asserion.test_strings">
                <stringProp name="0">404</stringProp>
              </collectionProp>
            </ResponseAssertion>
            <hashTree />
          </hashTree>
        </hashTree>
      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>
```

文件 `exercises/jmeter/day02_gui.ps1` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/08/day02/exercises/jmeter/day02_gui.ps1)

```powershell
param([string]$Jmeter = 'D:\tools\apache-jmeter-5.6.3\bin\jmeter.bat')
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Jmeter)) { throw 'JMeter路径错误' }
& $Jmeter -t performance/my_task_workflow.jmx
if ($LASTEXITCODE -ne 0) { throw 'GUI启动/运行异常，查看JMeter日志' }
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
& .\exercises\jmeter\day02_gui.ps1
```

**对照运行后的结果：** 默认1线程3轮19个样本，关联与断言正确；XML能解析仍不等于JMeter引擎已实际运行。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 能在 GUI 指出登录一次、每轮六次业务请求、提取器、headers、状态/业务断言、timer。
- [ ] 单线程调试成功；能解释每线程登录一次，因此 3 轮是 1+6×3=19 个样本。
- [ ] 自己的 JMX 不含硬编码任务 ID，调试监听器已关闭。

**卡住时：** token/id 为 MISSING 先看前置请求和提取表达式，不直接写死一个有效 ID。

<a id="day-3"></a>

## 第 3 天：非 GUI 执行，并检查样本数和 success

**材料：** JMeter 讲解第 3 节、`performance/jmeter.properties`、`tools/check_jtl.py`。

**操作与运行：** 确认保存了自己的计划、专用服务 health 正常。第一次使用下方目录，重做改成 smoke-02 等新名字：

```powershell
New-Item -ItemType Directory -Force reports/learning/jmeter/smoke-01
& $lessonJmeter -n -t performance/my_task_workflow.jmx -q performance/jmeter.properties -Jthreads=1 -Jloops=3 -Jramp_up=1 -Jthink_ms=200 -Jrun_id=smoke03 -l reports/learning/jmeter/smoke-01/results.jtl -j reports/learning/jmeter/smoke-01/jmeter.log -e -o reports/learning/jmeter/smoke-01/html
$LASTEXITCODE
.\.venv\Scripts\python.exe -m tools.check_jtl reports/learning/jmeter/smoke-01/results.jtl --expected-samples 19
$LASTEXITCODE
```

1. 打开 CSV JTL，找到 label/responseCode/success/elapsed；不要用电子表格保存覆盖原始 CSV。
2. 打开 HTML `index.html`，与检查器核对样本数量和失败数。
3. 解释为何预期 404 应 success=true，而任意 200 也可能因业务断言失败而 success=false。




<!-- daily-reference:start -->
**当天写完后的参考代码：**

common封装的是本周重复执行命令，显示了完整参数与退出码检查，不省略JTL门槛。今天脚本生成新目录smoke03；重做要换RunName。后续脚本都要先有这份common。

文件 `exercises/jmeter/common.ps1` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/08/day03/exercises/jmeter/common.ps1)

```powershell
$ErrorActionPreference = 'Stop'
$lessonRoot = (Resolve-Path "$PSScriptRoot/../..").Path
$lessonPython = Join-Path $lessonRoot '.venv/Scripts/python.exe'

function Invoke-LessonJmeter {
    param(
        [Parameter(Mandatory=$true)][string]$Jmeter,
        [Parameter(Mandatory=$true)][string]$Plan,
        [Parameter(Mandatory=$true)][string]$RunName,
        [int]$Threads = 1, [int]$Loops = 3,
        [int]$BusinessRequests = 6, [switch]$ExpectFailure
    )
    if (-not (Test-Path -LiteralPath $Jmeter)) { throw 'JMeter路径不存在' }
    if ($RunName -notmatch '^[A-Za-z0-9-]{1,30}$') { throw 'run_id限30位英数字或连字符' }
    if ($Threads -lt 1 -or $Loops -lt 1) { throw '线程数/循环数必须为正数' }
    $lessonDir = Join-Path $lessonRoot "reports/learning/jmeter/$RunName"
    if (Test-Path -LiteralPath $lessonDir) { throw '结果目录已存在，请换新RunName' }
    New-Item -ItemType Directory -Path $lessonDir | Out-Null
    $lessonHealth = Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8765/health
    if ($lessonHealth.StatusCode -ne 200) { throw '靶场未就绪' }
    & $Jmeter -n -t $Plan -q performance/jmeter.properties "-Jthreads=$Threads" "-Jloops=$Loops" "-Jramp_up=$Threads" -Jthink_ms=200 "-Jrun_id=$RunName" -l "$lessonDir/results.jtl" -j "$lessonDir/jmeter.log" -e -o "$lessonDir/html"
    $lessonJmeterExit = $LASTEXITCODE
    if ($lessonJmeterExit -ne 0) { throw "JMeter进程失败：$lessonJmeterExit" }
    $lessonExpected = $Threads * (1 + $BusinessRequests * $Loops)
    & $lessonPython -m tools.check_jtl "$lessonDir/results.jtl" --expected-samples $lessonExpected
    $lessonCheckExit = $LASTEXITCODE
    $lessonSamples = @(Import-Csv -LiteralPath "$lessonDir/results.jtl")
    $lessonFailures = @($lessonSamples | Where-Object { $_.success -eq 'false' }).Count
    if ($ExpectFailure) {
        if ($lessonCheckExit -eq 0 -or $lessonFailures -eq 0) { throw '没有验证到预期断言失败' }
        & $lessonPython -m tools.check_jtl "$lessonDir/results.jtl"
        if ($LASTEXITCODE -eq 0) { throw '包含失败样本却未返回非零' }
        Write-Output "预期故障成立：samples=$($lessonSamples.Count) failures=$lessonFailures"
    } else {
        if ($lessonCheckExit -ne 0) { throw 'JTL数量/断言检查失败' }
        Write-Output "通过：samples=$($lessonSamples.Count) failures=$lessonFailures expected=$lessonExpected"
    }
}

function Remove-LessonTasks {
    param([Parameter(Mandatory=$true)][string]$RunName)
    if ($RunName -notmatch '^[A-Za-z0-9-]{1,30}$') { throw 'run_id非法' }
    $lessonLogin = Invoke-RestMethod -Method Post -Uri http://127.0.0.1:8765/login -ContentType 'application/json' -Body '{"username":"alice","password":"alice-pass"}'
    $lessonHeaders = @{ Authorization = "Bearer $($lessonLogin.token)" }
    $lessonItems = (Invoke-RestMethod -Uri http://127.0.0.1:8765/tasks -Headers $lessonHeaders).items
    $lessonPrefix = "jm-$RunName-"
    $lessonTargets = @($lessonItems | Where-Object { $_.title.StartsWith($lessonPrefix) })
    foreach ($lessonTask in $lessonTargets) {
        Write-Output "清理本轮任务：id=$($lessonTask.id) title=$($lessonTask.title)"
        $lessonDelete = Invoke-WebRequest -UseBasicParsing -Method Delete -Uri "http://127.0.0.1:8765/tasks/$($lessonTask.id)" -Headers $lessonHeaders
        if ($lessonDelete.StatusCode -ne 204) { throw '资源清理失败' }
    }
    $lessonAfter = (Invoke-RestMethod -Uri http://127.0.0.1:8765/tasks -Headers $lessonHeaders).items
    if (@($lessonAfter | Where-Object { $_.title.StartsWith($lessonPrefix) }).Count -ne 0) { throw '仍有本轮残留' }
    Write-Output "run=$RunName 残留检查完成，本次清理$($lessonTargets.Count)条"
}
```

文件 `exercises/jmeter/day03_smoke.ps1` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/08/day03/exercises/jmeter/day03_smoke.ps1)

```powershell
param([string]$Jmeter = 'D:\tools\apache-jmeter-5.6.3\bin\jmeter.bat')
. "$PSScriptRoot/common.ps1"
Invoke-LessonJmeter -Jmeter $Jmeter -Plan performance/my_task_workflow.jmx -RunName smoke03
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
& .\exercises\jmeter\day03_smoke.ps1
```

**对照运行后的结果：** 19样本、0失败、检查器0；HTML在reports/learning/jmeter/smoke03/html/index.html。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] JTL 恰好 19 样本、0 failures，检查器退出 0；HTML 可读。
- [ ] 两个退出码分别记录，不把 JMeter 进程 0 当断言全通过。
- [ ] 结果目录与 run_id 唯一，JTL 没有混入旧数据。

**卡住时：** Dashboard 输出目录需不存在或为空；不要直接再次运行向旧 JTL 追加，再用旧样本伪装成功。

<a id="day-4"></a>

## 第 4 天：故意改错断言，验证检查器拦截

**操作：**

1. 把自己的正确计划另存为 `performance/my_task_workflow_bad.jmx`，在 `05_verify_update` 下将期望 HTTP 200 改成 201，只改这一处。
2. 用下方命令生成独立失败结果；失败会停止当前线程，因此可能少于 19 个样本：

```powershell
New-Item -ItemType Directory -Force reports/learning/jmeter/fail-01
& $lessonJmeter -n -t performance/my_task_workflow_bad.jmx -q performance/jmeter.properties -Jthreads=1 -Jloops=3 -Jramp_up=1 -Jthink_ms=200 -Jrun_id=fail04 -l reports/learning/jmeter/fail-01/results.jtl -j reports/learning/jmeter/fail-01/jmeter.log
$LASTEXITCODE
.\.venv\Scripts\python.exe -m tools.check_jtl reports/learning/jmeter/fail-01/results.jtl --expected-samples 19
$LASTEXITCODE
.\.venv\Scripts\python.exe -m tools.check_jtl reports/learning/jmeter/fail-01/results.jtl
$LASTEXITCODE
```

带数量参数的检查应拒绝缺样本；不带数量参数的检查应报告 failures>0 并非零退出。必须看到目标 sampler 的 success=false，只有缺样本不足以说明断言本身执行了。

3. 用阶段二的登录方法取得 Alice headers，GET `/tasks`，只筛选 title 以 `jm-fail04-` 开头的本次遗留任务，先核对 ID/title，再逐条 DELETE；GET 列表确认这些 ID 消失。在记录中保留残留数和清理结果，不删其他任务。
4. 正确的 `my_task_workflow.jmx` 保持正确；再按第 3 天命令换新目录 `recovered-01`、新 run_id 重跑通过。坏计划可保留，但文件名和说明必须明确是故障样例。




<!-- daily-reference:start -->
**当天写完后的参考代码：**

坏计划的05_verify_update实际200、故意期望201。停止线程会留下任务，所以先检查success=false、再仅按本轮前缀清理，最后用正确计划在新目录重跑。

文件 `performance/my_task_workflow_bad.jmx` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/08/day04/performance/my_task_workflow_bad.jmx)

故意失败计划；正确计划保持不变。完整XML便于直接对照仅改错的断言。

```xml
<?xml version='1.0' encoding='utf-8'?>
<jmeterTestPlan version="1.2" properties="5.0" jmeter="5.6.3">
  <hashTree>
    <TestPlan guiclass="TestPlanGui" testclass="TestPlan" testname="Local task API workflow" enabled="true">
      <stringProp name="TestPlan.comments">Local training only. Default: 1 thread, 3 loops, 19 samples. Stop thread on failure.</stringProp>
      <boolProp name="TestPlan.functional_mode">false</boolProp>
      <boolProp name="TestPlan.serialize_threadgroups">false</boolProp>
      <elementProp name="TestPlan.user_defined_variables" elementType="Arguments" guiclass="ArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
        <collectionProp name="Arguments.arguments" />
      </elementProp>
    </TestPlan>
    <hashTree>
      <ThreadGroup guiclass="ThreadGroupGui" testclass="ThreadGroup" testname="Task users" enabled="true">
        <stringProp name="ThreadGroup.on_sample_error">stopthread</stringProp>
        <elementProp name="ThreadGroup.main_controller" elementType="LoopController" guiclass="LoopControlPanel" testclass="LoopController" testname="Loop Controller" enabled="true">
          <boolProp name="LoopController.continue_forever">false</boolProp>
          <stringProp name="LoopController.loops">${__P(loops,3)}</stringProp>
        </elementProp>
        <stringProp name="ThreadGroup.num_threads">${__P(threads,1)}</stringProp>
        <stringProp name="ThreadGroup.ramp_time">${__P(ramp_up,1)}</stringProp>
        <stringProp name="ThreadGroup.duration" />
        <stringProp name="ThreadGroup.delay" />
        <boolProp name="ThreadGroup.scheduler">false</boolProp>
        <boolProp name="ThreadGroup.same_user_on_next_iteration">true</boolProp>
      </ThreadGroup>
      <hashTree>
        <ConfigTestElement guiclass="HttpDefaultsGui" testclass="ConfigTestElement" testname="HTTP defaults" enabled="true">
          <stringProp name="HTTPSampler.domain">${__P(host,127.0.0.1)}</stringProp>
          <stringProp name="HTTPSampler.port">${__P(port,8765)}</stringProp>
          <stringProp name="HTTPSampler.protocol">http</stringProp>
          <stringProp name="HTTPSampler.contentEncoding">UTF-8</stringProp>
          <stringProp name="HTTPSampler.connect_timeout">3000</stringProp>
          <stringProp name="HTTPSampler.response_timeout">5000</stringProp>
          <stringProp name="HTTPSampler.implementation">HttpClient4</stringProp>
          <elementProp name="HTTPsampler.Arguments" elementType="Arguments" guiclass="HTTPArgumentsPanel" testclass="Arguments" testname="User Defined Variables" enabled="true">
            <collectionProp name="Arguments.arguments" />
          </elementProp>
        </ConfigTestElement>
        <hashTree />
        <HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="JSON headers" enabled="true">
          <collectionProp name="HeaderManager.headers">
            <elementProp name="" elementType="Header">
              <stringProp name="Header.name">Content-Type</stringProp>
              <stringProp name="Header.value">application/json</stringProp>
            </elementProp>
          </collectionProp>
        </HeaderManager>
        <hashTree />
        <OnceOnlyController guiclass="OnceOnlyControllerGui" testclass="OnceOnlyController" testname="Login once per thread" enabled="true" />
        <hashTree>
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="01_login" enabled="true">
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
              <collectionProp name="Arguments.arguments">
                <elementProp name="" elementType="HTTPArgument">
                  <boolProp name="HTTPArgument.always_encode">false</boolProp>
                  <stringProp name="Argument.value">{"username":"alice","password":"alice-pass"}</stringProp>
                  <stringProp name="Argument.metadata">=</stringProp>
                </elementProp>
              </collectionProp>
            </elementProp>
            <boolProp name="HTTPSampler.postBodyRaw">true</boolProp>
            <stringProp name="HTTPSampler.path">/login</stringProp>
            <stringProp name="HTTPSampler.method">POST</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">false</boolProp>
            <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          </HTTPSamplerProxy>
          <hashTree>
            <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Expect HTTP 200" enabled="true">
              <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
              <boolProp name="Assertion.assume_success">true</boolProp>
              <intProp name="Assertion.test_type">8</intProp>
              <collectionProp name="Asserion.test_strings">
                <stringProp name="0">200</stringProp>
              </collectionProp>
            </ResponseAssertion>
            <hashTree />
            <JSONPostProcessor guiclass="JSONPostProcessorGui" testclass="JSONPostProcessor" testname="Extract thread token" enabled="true">
              <stringProp name="JSONPostProcessor.referenceNames">auth_token</stringProp>
              <stringProp name="JSONPostProcessor.jsonPathExprs">$.token</stringProp>
              <stringProp name="JSONPostProcessor.match_numbers">1</stringProp>
              <stringProp name="JSONPostProcessor.defaultValues">MISSING</stringProp>
              <boolProp name="JSONPostProcessor.compute_concat">false</boolProp>
            </JSONPostProcessor>
            <hashTree />
          </hashTree>
        </hashTree>
        <GenericController guiclass="LogicControllerGui" testclass="GenericController" testname="Task business workflow" enabled="true" />
        <hashTree>
          <HeaderManager guiclass="HeaderPanel" testclass="HeaderManager" testname="Bearer token" enabled="true">
            <collectionProp name="HeaderManager.headers">
              <elementProp name="" elementType="Header">
                <stringProp name="Header.name">Authorization</stringProp>
                <stringProp name="Header.value">Bearer ${auth_token}</stringProp>
              </elementProp>
            </collectionProp>
          </HeaderManager>
          <hashTree />
          <ConstantTimer guiclass="ConstantTimerGui" testclass="ConstantTimer" testname="Think time before each business request" enabled="true">
            <stringProp name="ConstantTimer.delay">${__P(think_ms,200)}</stringProp>
          </ConstantTimer>
          <hashTree />
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="02_create" enabled="true">
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
              <collectionProp name="Arguments.arguments">
                <elementProp name="" elementType="HTTPArgument">
                  <boolProp name="HTTPArgument.always_encode">false</boolProp>
                  <stringProp name="Argument.value">{"title":"jm-${__P(run_id,local)}-${__threadNum}-${__counter(FALSE,)}"}</stringProp>
                  <stringProp name="Argument.metadata">=</stringProp>
                </elementProp>
              </collectionProp>
            </elementProp>
            <boolProp name="HTTPSampler.postBodyRaw">true</boolProp>
            <stringProp name="HTTPSampler.path">/tasks</stringProp>
            <stringProp name="HTTPSampler.method">POST</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">false</boolProp>
            <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          </HTTPSamplerProxy>
          <hashTree>
            <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Expect HTTP 201" enabled="true">
              <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
              <boolProp name="Assertion.assume_success">true</boolProp>
              <intProp name="Assertion.test_type">8</intProp>
              <collectionProp name="Asserion.test_strings">
                <stringProp name="0">201</stringProp>
              </collectionProp>
            </ResponseAssertion>
            <hashTree />
            <JSONPostProcessor guiclass="JSONPostProcessorGui" testclass="JSONPostProcessor" testname="Extract task ID" enabled="true">
              <stringProp name="JSONPostProcessor.referenceNames">task_id</stringProp>
              <stringProp name="JSONPostProcessor.jsonPathExprs">$.id</stringProp>
              <stringProp name="JSONPostProcessor.match_numbers">1</stringProp>
              <stringProp name="JSONPostProcessor.defaultValues">MISSING</stringProp>
              <boolProp name="JSONPostProcessor.compute_concat">false</boolProp>
            </JSONPostProcessor>
            <hashTree />
          </hashTree>
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="03_read" enabled="true">
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
              <collectionProp name="Arguments.arguments" />
            </elementProp>
            <stringProp name="HTTPSampler.path">/tasks/${task_id}</stringProp>
            <stringProp name="HTTPSampler.method">GET</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">false</boolProp>
            <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          </HTTPSamplerProxy>
          <hashTree>
            <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Expect HTTP 200" enabled="true">
              <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
              <boolProp name="Assertion.assume_success">true</boolProp>
              <intProp name="Assertion.test_type">8</intProp>
              <collectionProp name="Asserion.test_strings">
                <stringProp name="0">200</stringProp>
              </collectionProp>
            </ResponseAssertion>
            <hashTree />
          </hashTree>
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="04_update" enabled="true">
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
              <collectionProp name="Arguments.arguments">
                <elementProp name="" elementType="HTTPArgument">
                  <boolProp name="HTTPArgument.always_encode">false</boolProp>
                  <stringProp name="Argument.value">{"status":"done"}</stringProp>
                  <stringProp name="Argument.metadata">=</stringProp>
                </elementProp>
              </collectionProp>
            </elementProp>
            <boolProp name="HTTPSampler.postBodyRaw">true</boolProp>
            <stringProp name="HTTPSampler.path">/tasks/${task_id}</stringProp>
            <stringProp name="HTTPSampler.method">PUT</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">false</boolProp>
            <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          </HTTPSamplerProxy>
          <hashTree>
            <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Expect HTTP 200" enabled="true">
              <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
              <boolProp name="Assertion.assume_success">true</boolProp>
              <intProp name="Assertion.test_type">8</intProp>
              <collectionProp name="Asserion.test_strings">
                <stringProp name="0">200</stringProp>
              </collectionProp>
            </ResponseAssertion>
            <hashTree />
          </hashTree>
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="05_verify_update" enabled="true">
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
              <collectionProp name="Arguments.arguments" />
            </elementProp>
            <stringProp name="HTTPSampler.path">/tasks/${task_id}</stringProp>
            <stringProp name="HTTPSampler.method">GET</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">false</boolProp>
            <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          </HTTPSamplerProxy>
          <hashTree>
            <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Intentionally wrong HTTP 201" enabled="true">
              <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
              <boolProp name="Assertion.assume_success">true</boolProp>
              <intProp name="Assertion.test_type">8</intProp>
              <collectionProp name="Asserion.test_strings">
                <stringProp name="0">201</stringProp>
              </collectionProp>
            </ResponseAssertion>
            <hashTree />
            <JSR223Assertion guiclass="TestBeanGUI" testclass="JSR223Assertion" testname="Persisted task must be done" enabled="true">
              <stringProp name="scriptLanguage">groovy</stringProp>
              <stringProp name="parameters" />
              <stringProp name="filename" />
              <stringProp name="cacheKey">true</stringProp>
              <stringProp name="script">def task = new groovy.json.JsonSlurper().parseText(prev.getResponseDataAsString())
if (task.status != 'done' || task.id.toString() != vars.get('task_id')) {
    AssertionResult.setFailure(true)
    AssertionResult.setFailureMessage('Expected current task ID and persisted status=done')
}
</stringProp>
            </JSR223Assertion>
            <hashTree />
          </hashTree>
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="06_delete" enabled="true">
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
              <collectionProp name="Arguments.arguments" />
            </elementProp>
            <stringProp name="HTTPSampler.path">/tasks/${task_id}</stringProp>
            <stringProp name="HTTPSampler.method">DELETE</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">false</boolProp>
            <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          </HTTPSamplerProxy>
          <hashTree>
            <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Expect HTTP 204" enabled="true">
              <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
              <boolProp name="Assertion.assume_success">true</boolProp>
              <intProp name="Assertion.test_type">8</intProp>
              <collectionProp name="Asserion.test_strings">
                <stringProp name="0">204</stringProp>
              </collectionProp>
            </ResponseAssertion>
            <hashTree />
          </hashTree>
          <HTTPSamplerProxy guiclass="HttpTestSampleGui" testclass="HTTPSamplerProxy" testname="07_verify_deleted" enabled="true">
            <elementProp name="HTTPsampler.Arguments" elementType="Arguments">
              <collectionProp name="Arguments.arguments" />
            </elementProp>
            <stringProp name="HTTPSampler.path">/tasks/${task_id}</stringProp>
            <stringProp name="HTTPSampler.method">GET</stringProp>
            <boolProp name="HTTPSampler.follow_redirects">false</boolProp>
            <boolProp name="HTTPSampler.auto_redirects">false</boolProp>
            <boolProp name="HTTPSampler.use_keepalive">true</boolProp>
            <boolProp name="HTTPSampler.DO_MULTIPART_POST">false</boolProp>
          </HTTPSamplerProxy>
          <hashTree>
            <ResponseAssertion guiclass="AssertionGui" testclass="ResponseAssertion" testname="Expect HTTP 404" enabled="true">
              <stringProp name="Assertion.test_field">Assertion.response_code</stringProp>
              <boolProp name="Assertion.assume_success">true</boolProp>
              <intProp name="Assertion.test_type">8</intProp>
              <collectionProp name="Asserion.test_strings">
                <stringProp name="0">404</stringProp>
              </collectionProp>
            </ResponseAssertion>
            <hashTree />
          </hashTree>
        </hashTree>
      </hashTree>
    </hashTree>
  </hashTree>
</jmeterTestPlan>
```

文件 `exercises/jmeter/day04_failure.ps1` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/08/day04/exercises/jmeter/day04_failure.ps1)

```powershell
param([string]$Jmeter = 'D:\tools\apache-jmeter-5.6.3\bin\jmeter.bat')
. "$PSScriptRoot/common.ps1"
Invoke-LessonJmeter -Jmeter $Jmeter -Plan performance/my_task_workflow_bad.jmx -RunName fail04 -ExpectFailure
Remove-LessonTasks -RunName fail04
Invoke-LessonJmeter -Jmeter $Jmeter -Plan performance/my_task_workflow.jmx -RunName recovered04
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
& .\exercises\jmeter\day04_failure.ps1
```

**对照运行后的结果：** 坏计划检查器非零且有失败样本；残留清理；recovered04为19成功样本。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 原始失败 JTL、目标失败 label、检查器非零退出都保存。
- [ ] 恢复的正确计划产生 19 个成功样本，失败残留已按 run_id 清理。
- [ ] 能解释“停止线程”为什么会同时导致样本缺失。

**卡住时：** 创建后的断言失败会留下数据；不能仅重跑成功就认定旧残留已清理。

<a id="day-5"></a>

## 第 5 天：做 1/2/5 线程的可比较实验

**材料：** JMeter 讲解第 4 节、报告模板。

**操作：**

1. 确认前四天功能与清理验收都通过，关闭 GUI 和结果树，记录服务初始数据量。
2. 同一环境、同一计划、每线程 10 轮、think_ms=200；ramp-up 分别 1/2/5 秒。以下循环串行执行三档，不同时启动三场负载：

```powershell
foreach ($lessonThreads in 1, 2, 5) {
    $lessonDir = "reports/learning/jmeter/t${lessonThreads}-01"
    New-Item -ItemType Directory -Force $lessonDir
    & $lessonJmeter -n -t performance/my_task_workflow.jmx -q performance/jmeter.properties "-Jthreads=$lessonThreads" -Jloops=10 "-Jramp_up=$lessonThreads" -Jthink_ms=200 "-Jrun_id=t${lessonThreads}day05" -l "$lessonDir/results.jtl" -j "$lessonDir/jmeter.log" -e -o "$lessonDir/html"
    $lessonJmeterExit = $LASTEXITCODE
    $lessonExpected = $lessonThreads * 61
    .\.venv\Scripts\python.exe -m tools.check_jtl "$lessonDir/results.jtl" --expected-samples $lessonExpected
    $lessonCheckExit = $LASTEXITCODE
    "threads=$lessonThreads jmeter_exit=$lessonJmeterExit check_exit=$lessonCheckExit"
    if ($lessonJmeterExit -ne 0 -or $lessonCheckExit -ne 0) { break }
}
```

3. 每档预期样本数为 61/122/305，分别记录实际数量、失败数、执行窗口。失败先定位，不继续加线程；修复后用新目录重测。
4. 同时用任务管理器或另一个终端记录 CPU/内存/磁盘的时间窗口，注明客户端服务同机。




<!-- daily-reference:start -->
**当天写完后的参考代码：**

三档串行执行，除线程与ramp-up外条件保持一致；common遇到任一异常会抛错，不继续压下一档。名称同时用作结果目录和run_id，方便追溯清理。

文件 `exercises/jmeter/day05_load.ps1` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/08/day05/exercises/jmeter/day05_load.ps1)

```powershell
param([string]$Jmeter = 'D:\tools\apache-jmeter-5.6.3\bin\jmeter.bat')
. "$PSScriptRoot/common.ps1"
foreach ($lessonThreads in 1, 2, 5) {
    Invoke-LessonJmeter -Jmeter $Jmeter -Plan performance/my_task_workflow.jmx -RunName "t${lessonThreads}day05" -Threads $lessonThreads -Loops 10
}
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
& .\exercises\jmeter\day05_load.ps1
```

**对照运行后的结果：** 三档分别61/122/305样本、0失败；资源观测由你在相同时间窗记录。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 三档各有独立 JTL/HTML、数量正确、检查器为 0，条件差异均写明。
- [ ] 能解释线程数不是 QPS、思考时间会影响吞吐。
- [ ] 有同时间窗资源观测，没有只凭慢就归因数据库。

**卡住时：** 新终端需重新设置 `$lessonJmeter`；循环只执行一档时查退出码与 break 原因，不填造其余两档结果。

<a id="day-6"></a>

## 第 6 天：按接口分析指标，填写报告

**材料：** `performance/REPORT_TEMPLATE.md`、三档 JTL/HTML。

**操作：**

1. 复制模板为 `performance/my_report.md`，填写真实环境、参数、样本数、目标与限制。
2. 从检查器按 label 取得样本数、失败数和 nearest-rank P95；从 Dashboard 读取相同 label 的吞吐与时间单位。每个数字标明来自哪份结果与哪个统计口径。
3. 选 create、verify_update 两个接口比较三档；不要将登录与 CRUD 混成一个平均数后断言所有接口都快。
4. 解释 P95、平均值、错误率的区别；若 Dashboard 与检查器 P95 不同，检查百分位算法、小样本与统计窗口，不直接修改原始结果。




<!-- daily-reference:start -->
**当天写完后的参考代码：**

指标脚本读取真实JTL并验证样本与失败数，缺文件会报错，不造数据。报告文字完整说明实验方法和指标口径；最后的实际环境、观察与结论仍需你据证据填写。

文件 `exercises/jmeter/report_metrics.py` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/08/day06/exercises/jmeter/report_metrics.py)

```python
import argparse
import csv
import math
from pathlib import Path
from collections import defaultdict
from tools.check_jtl import summarize

parser = argparse.ArgumentParser()
parser.add_argument("--root", type=Path, default=Path("reports/learning/jmeter"))
parser.add_argument("--output", type=Path, default=Path("performance/my_metrics.md"))
args = parser.parse_args()
if args.output.exists():
    parser.error("输出已存在，请用--output指定新文件，避免覆盖个人报告")
lines = ["# 本轮真实JTL指标", "", "P95采用nearest-rank；吞吐单位samples/s，按每个label自身首样本开始至末样本结束的窗口计算。", "",
    "| 线程 | label | 样本 | 失败 | 错误率 | P95 ms | 吞吐 samples/s |",
    "|---|---|---|---|---|---|---|"]
for threads in (1, 2, 5):
    path = args.root / f"t{threads}day05/results.jtl"
    summary = summarize(path, threads * 61)
    assert summary["failures"] == 0, f"{path}有失败，先分析原因"
    groups = defaultdict(list)
    with path.open(encoding="utf-8-sig", newline="") as stream:
        for row in csv.DictReader(stream):
            groups[row["label"]].append(row)
    for label, rows in sorted(groups.items()):
        elapsed = sorted(int(row["elapsed"]) for row in rows)
        p95 = elapsed[math.ceil(len(elapsed) * 0.95) - 1]
        first = min(int(row["timeStamp"]) for row in rows)
        last = max(int(row["timeStamp"]) + int(row["elapsed"]) for row in rows)
        seconds = (last - first) / 1000
        throughput = f"{len(rows) / seconds:.2f}" if seconds > 0 else "窗口为0，不能计算"
        lines.append(f"| {threads} | {label} | {len(rows)} | 0 | 0% | {p95} | {throughput} |")
lines += ["", "数据来自各档独立JTL。不同于Dashboard口径时先对照时间窗和算法，不篡改原始数据。", "",
          "此表仅为本机实验指标，不证明线上容量；环境、资源观测和原因分析另见my_report.md。"]
args.output.parent.mkdir(parents=True, exist_ok=True)
args.output.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("已生成：", args.output)
```

文件 `performance/my_report.md` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/08/day06/performance/my_report.md)

```markdown
# 我的本机负载实验报告（参考写法）

目标：比较相同业务比例与200ms思考时间下1/2/5线程现象。
计划：my_task_workflow.jmx；每线程登录1次，每轮6请求，每线程10轮。
预期样本：61/122/305；实际值引用my_metrics.md及各原始JTL，不填虚构数字。
方法：同机客户端与服务、Python标准库HTTP+SQLite、各档串行执行；ramp-up为1/2/5秒。
P95口径：nearest-rank，按label；吞吐口径见my_metrics.md，单位samples/s。
清理：按各run_id的jm-前缀核对残留，仅回收本轮资源。
限制：短时小样本、同机干扰、教学数据库，不能推导线上容量或最大QPS。
本人实际环境/时间/代码版本、CPU内存磁盘观测、重复测量、观察与待验证假设：运行后填写。
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
.\.venv\Scripts\python.exe -m exercises.jmeter.report_metrics
```

**对照运行后的结果：** python -m exercises.jmeter.report_metrics生成真实21行label对比（原计划7个label×3档），不是预填性能数字。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 报告没有空白占位数字，至少两个 label 的三档样本、失败数、P95、吞吐及单位可追溯。
- [ ] 明确本机 SQLite 短测不能给出线上容量、最大 QPS 或生产 SLA 结论。
- [ ] 每个原因判断都有证据或标为待验证假设。

**卡住时：** 检查器仅提供部分指标，不会计算所有 Dashboard 指标；不把工具没有输出的数据编出来。

<a id="day-7"></a>

## 第 7 天：重复一档、核对残留并交付

**操作：**

1. 按第 5 天条件重复 2 线程×10 轮，使用新目录 t2-02、新 run_id，预期 122 样本；记录与 t2-01 的波动，不挑最好的一次。
2. 登录专用服务，按本周各 run_id 前缀核对遗留，逐个处理并写结果；核对后停止自己的手动服务。
3. 在 `docs/jmeter_practice.md` 索引自己的正确/故障 JMX、成功/失败/重复 JTL、检查器退出码、报告和清理记录。




<!-- daily-reference:start -->
**当天写完后的参考代码：**

重复同一档仍用新run_id；保留两次结果比较波动，不挑快的一次。清理脚本逐前缀处理，输出实际残留数；最后手动Ctrl+C停止终端A的专用服务。

文件 `exercises/jmeter/day07_repeat.ps1` — 新建此文件；已存在时对照合并，以下是本日完整版本。 [打开参考文件](reference/08/day07/exercises/jmeter/day07_repeat.ps1)

```powershell
param([string]$Jmeter = 'D:\tools\apache-jmeter-5.6.3\bin\jmeter.bat')
. "$PSScriptRoot/common.ps1"
Invoke-LessonJmeter -Jmeter $Jmeter -Plan performance/my_task_workflow.jmx -RunName t2repeat07 -Threads 2 -Loops 10
foreach ($lessonRun in 'smoke03', 'fail04', 'recovered04', 't1day05', 't2day05', 't5day05', 't2repeat07') {
    Remove-LessonTasks -RunName $lessonRun
}
Write-Output '保留重复测量和清理输出；回终端A按Ctrl+C停止本周专用服务。'
```

**运行本日参考代码（项目根目录，PowerShell）：**

```powershell
& .\exercises\jmeter\day07_repeat.ps1
```

**对照运行后的结果：** 重复档122成功样本，各轮残留核对完成；成功/失败/恢复/重复JTL都保留。

代码抄完后，还要完成下面的验收；“能运行”与“能解释、能修改输入重做”分别核对。

<!-- daily-reference:end -->

**完成判定：**

- [ ] 正确与故意失败两条验证链完整，重复档位也检查数量/断言。
- [ ] 报告可追溯到原始 JTL，残留已核对；没有把临时 token 写进附件。
- [ ] 不看教程能解释 token/ID 关联、19/61/122/305 的计算与一项指标限制。

**未通过怎么办：** 关联错误回第 2 天；只看进程退出码回第 3—4 天；实验不可比回第 5 天；结论超证据回第 6 天。
