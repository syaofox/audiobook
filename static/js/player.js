document.addEventListener('DOMContentLoaded', function() {
    const audioPlayer = document.getElementById('audio-player');
    const textDisplay = document.getElementById('text-display');
    const audioList = document.getElementById('audio-list');
    
    let currentAudio = '';

    // 从localStorage加载上次的播放进度
    function loadProgress() {
        const savedTime = localStorage.getItem(`audioProgress_${currentAudio}`);
        if (savedTime) {
            audioPlayer.currentTime = parseFloat(savedTime);
        }
    }

    // 保存播放进度
    function saveProgress() {
        localStorage.setItem(`audioProgress_${currentAudio}`, audioPlayer.currentTime);
    }

    // 加载文本内容
    async function loadText(textFile) {
        try {
            const response = await fetch(`/get_text/${textFile}`);
            const data = await response.json();
            if (data.status === 'success') {
                textDisplay.textContent = data.content;
            } else {
                textDisplay.textContent = '暂无文本内容';
            }
        } catch (error) {
            console.error('Error:', error);
            textDisplay.textContent = '暂无文本内容';
        }
    }

    // 点击播放列表项
    audioList.addEventListener('click', function(e) {
        if (e.target.tagName === 'LI') {
            const audioSrc = e.target.dataset.audio;
            const textFile = e.target.dataset.text;
            
            // 保存当前音频的进度
            if (currentAudio) {
                saveProgress();
            }
            
            // 更新音频源并播放（不等待文本加载）
            audioPlayer.src = audioSrc;
            currentAudio = audioSrc;
            loadProgress();
            audioPlayer.play();
            
            // 异步加载文本，不影响音频播放
            loadText(textFile).catch(() => {
                textDisplay.textContent = '暂无文本内容';
            });
        }
    });

    // 定期保存进度
    audioPlayer.addEventListener('timeupdate', function() {
        if (currentAudio) {
            saveProgress();
        }
    });
}); 