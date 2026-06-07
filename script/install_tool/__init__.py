"""easy-dev 跨平台工具链安装包。

依赖方向：CLI -> factory -> core 抽象 <- 各平台实现 (windows / linux)。
平台实现彼此隔离，且只在对应平台被 factory 导入。
"""
