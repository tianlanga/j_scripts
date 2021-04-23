#!/usr/bin/env bash
downpath=$JD_DIR/own/download
monkpath=$JD_DIR/own/monkcoder_dust

! <<!
嘎嘎嘎嘎嘎
【功能】
自动遍历下载monk-coder的js文件
会自动把新增文件拷贝到own/monkcoder_dust目录
会按照MD5比对后更新，不会每次全部覆盖
E大V4会自动按照文件加入到定时任务里
目前不会删除过期脚本，自己手动删吧
由于monk-coder是转链的谷歌盘,连接不稳定，网络原因有时候会下载错误或者连接异常，我已尽可能的排错了，错误文件将不会替换到更新目录内！
【使用说明】
不要改目录定义，目录都是容器里的，不是针对真实系统的！！！
不要改目录定义，目录都是容器里的，不是针对真实系统的！！！
不要改目录定义，目录都是容器里的，不是针对真实系统的！！！
1.把download.sh复制到容器内的/jd/config下面
2.给download.sh运行权限，执行指令：chmod 644 download.sh
3.config.sh Own库地方加入如下配置,当然是不能更新的，目的是让V4脚本脚本自动添加删除定时任务
  OwnRepoUrl1="git@monk_github:monkcoder/dust.git" 
  OwnRepoBranch1=""
  OwnRepoPath1=""
  AutoAddOwnCron="true"
  AutoDelOwnCron="true"
4.以后都设置好后先手动执行一次download.sh，如果没问题的话再运行jup就能添加删除定时任务
  容器外面用这条运行脚本 docker exec -it jd bash /jd/config/download.sh
  容器内用这条运行脚本 bash $JD_DIR/config/download.sh
5.没必要加入diy脚本里面，容器定时列表加入如下定时任务，库更新频率不会很高，建议几个小时执行一次，减少服务器压力
  20 8-18/3 * * * bash $JD_DIR/config/download.sh  >> $JD_DIR/log/Download.log 2>&1
设置好后，以后就能定时更新脚本并自动添加新的定时任务了。
!

function monkcoder() {
	#创建download文件夹
	if [[ ! -d $downpath ]]; then
		mkdir $downpath
	fi
	#创建monk_coder文件夹
	if [[ ! -d $monkpath ]]; then
		mkdir $monkpath
	fi

	i=1

	while [ "$i" -le 5 ]; do
		folders="$(curl -sX POST "https://share.r2ray.com/dust/" | grep -oP "name.*?\.folder" | cut -d, -f1 | cut -d\" -f3 | grep -vE "backup|pics|rewrite" | tr "\n" " ")"
		test -n "$folders" && {
			rm -rf $downpath/*
			break
		} || {
			echo 第 $i/5 次目录列表获取失败
			i=$((i + 1))
			sleep $((1+($RANDOM%5)))
		}
	done

	for folder in $folders; do
		i=1
		while [ "$i" -le 5 ]; do
			jsnames="$(curl -sX POST "https://share.r2ray.com/dust/${folder}/" | grep -oP "name.*?\.js\"" | grep -oE "[^\"]*\.js\"" | cut -d\" -f1 | tr "\n" " ")"
			test -n "$jsnames" && break || {
				echo 第 $i/5 次 $folder 目录下文件列表获取失败
				i=$((i + 1))
				sleep $((1+($RANDOM%5)))
			}
		done

		if [ "$i" -eq 5 ]; then
			continue
		fi

		cd $downpath

		for jsname in $jsnames; do
			i=1
			while [ "$i" -le 5 ]; do
				curl -so ${jsname} "https://share.r2ray.com/dust/${folder}/${jsname}"
				test "$(wc -c <"${jsname}")" -ge 500 && {
					#连接错误后会把错误提示页面下载成Js文件，捕获错误页面内容并排除
					grep "What happened?" $downpath/$jsname >>/dev/null
					if [ $? -ne 0 ]; then
						#echo -e "已下载["$folder"]目录中的["$jsname"]文件."
						#判断是否新增脚本
						if [ ! -f "$monkpath/$jsname" ]; then
							cp $downpath/$jsname $monkpath/
							echo -e "新增加文件"$jsname
						else
							md5download=$(md5sum $downpath/$jsname | cut -d ' ' -f1)
							md5monkcoder=$(md5sum $monkpath/$jsname | cut -d ' ' -f1)
							#echo -e "md5download_"$jsname":"$md5download
							#echo -e "md5monkcode_"$jsname":"$md5monkcoder
							#判断已存在的脚本是否更新了内容
							if [[ $md5download != $md5monkcoder ]]; then
								yes | cp -rf $downpath/$jsname $monkpath/
								echo -e "更新文件"$jsname
							fi
						fi
						break
					else
						#echo -e $jsname"下载地址错误,页面404！！！"
						echo 第 $i/5 次 $folder 目录下 $jsname 文件下载失败
						i=$((i + 1))
					     sleep $((1+($RANDOM%5)))
					fi
				} || {
					echo 第 $i/5 次 $folder 目录下 $jsname 文件下载失败
					i=$((i + 1))
					sleep $((1+($RANDOM%5)))
				}
			done

			if [ "$i" -eq 5 ]; then
				continue
			fi

			#echo $folder/$jsname文件下载成功
		done
	done
}

function main() {
     echo "---------------------------------------------------------------------"
     echo "系统时间:" $(date +"%Y-%m-%d %H:%M:%S")
     echo "---------------------------------------------------------------------"
	apk add --no-cache --upgrade grep
	monkcoder
}

main
