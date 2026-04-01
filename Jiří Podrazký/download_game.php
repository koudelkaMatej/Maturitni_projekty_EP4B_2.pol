<?php
session_start();

$folderName = 'hra';
$zipName = 'SpaceInvaders_Enterprise.zip';
$folderPath = realpath(__DIR__ . DIRECTORY_SEPARATOR . $folderName);

if (!$folderPath || !is_dir($folderPath)) {
    die("Error: Source folder 'hra' not found.");
}

// Vyhneme sa /tmp kvoli open_basedir restrikciám na hostingu
// Vytvoríme temp súbor v aktuálnom priečinku
$tempZip = __DIR__ . DIRECTORY_SEPARATOR . 'game_' . uniqid() . '.zip';

// Pokus 1: ZipArchive
if (class_exists('ZipArchive')) {
    $zip = new ZipArchive();
    if ($zip->open($tempZip, ZipArchive::CREATE | ZipArchive::OVERWRITE) === TRUE) {
        $files = new RecursiveIteratorIterator(
            new RecursiveDirectoryIterator($folderPath, RecursiveDirectoryIterator::SKIP_DOTS),
            RecursiveIteratorIterator::LEAVES_ONLY
        );
        foreach ($files as $name => $file) {
            $filePath = $file->getRealPath();
            $relativePath = substr($filePath, strlen($folderPath) + 1);
            $zip->addFile($filePath, $relativePath);
        }
        $zip->close();
    }
}

// Pokus 2: Systémový príkaz 'zip'
if (!file_exists($tempZip) || filesize($tempZip) == 0) {
    if (function_exists('shell_exec')) {
        $cmd = "cd " . escapeshellarg($folderPath) . " && zip -r " . escapeshellarg($tempZip) . " . 2>&1";
        $output = shell_exec($cmd);
        // Ak sa nepodarilo, môžeme aspoň debugovať (zakomentované pre produkciu)
        // file_put_contents('zip_error.log', $output);
    }
}

// Ak súbor podarilo vytvoriť, odošleme ho
if (file_exists($tempZip) && filesize($tempZip) > 0) {
    header('Content-Type: application/zip');
    header('Content-Disposition: attachment; filename="' . $zipName . '"');
    header('Content-Length: ' . filesize($tempZip));
    header('Pragma: no-cache');
    header('Expires: 0');

    readfile($tempZip);
    unlink($tempZip); // Zmažeme po stiahnutí
    exit;
} else {
    // Ak ani jedno nefunguje, vypíšeme zrozumiteľnú chybu pre hosting
    die("Error: Na tomto serveru chybí rozšíření PHP 'zip' a systémové volání 'shell_exec' je zakázáno nebo omezeno restrikcí open_basedir. <br><br><b>Řešení:</b> Poproste administrátora o povolení PHP ZipArchive, nebo mi dovolte vytvořit statický soubor .zip manuálně.");
}
?>
