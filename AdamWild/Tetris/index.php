<?php
// Načtení připojení k databázi
require_once 'pripojeni.php';

// Získání připojení
$conn = get_db_connection();

// Načtení highscores z databáze
$sql = "SELECT jmeno, skore, datum FROM tetris_highscores ORDER BY skore DESC LIMIT 20";
$result = $conn->query($sql);

$highscores = [];
if ($result && $result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        $highscores[] = $row;
    }
}

$conn->close();
?>
<!DOCTYPE html>
<html lang="cs">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tetris - Žebříček</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: Arial, sans-serif;
            background: #2a5298;
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
            max-width: 700px;
            width: 100%;
            padding: 30px;
        }
        
        h1 {
            text-align: center;
            color: #1e3c72;
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 1em;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }
        
        th {
            background: #1e3c72;
            color: white;
            padding: 12px;
            text-align: left;
            font-weight: bold;
        }
        
        th:first-child {
            border-radius: 5px 0 0 0;
            text-align: center;
            width: 80px;
        }
        
        th:last-child {
            border-radius: 0 5px 0 0;
            text-align: right;
            width: 120px;
        }
        
        td {
            padding: 12px;
            border-bottom: 1px solid #eee;
        }
        
        td:first-child {
            text-align: center;
            font-weight: bold;
            color: #1e3c72;
        }
        
        td:last-child {
            text-align: right;
        }
        
        td:nth-child(3) {
            text-align: right;
            font-weight: bold;
        }
        
        tr:hover {
            background: #f5f5f5;
        }
        
        .refresh-btn {
            display: block;
            margin: 20px auto 0;
            padding: 12px 30px;
            background: #1e3c72;
            color: white;
            border: none;
            border-radius: 5px;
            font-size: 1em;
            cursor: pointer;
            text-decoration: none;
        }
        
        .refresh-btn:hover {
            background: #2a5298;
        }
        
        .no-scores {
            text-align: center;
            color: #999;
            padding: 40px;
            font-size: 1.1em;
        }
        
        .last-updated {
            text-align: center;
            color: #999;
            margin-top: 15px;
            font-size: 0.85em;
        }
        
        .date {
            color: #999;
            font-size: 0.85em;
        }
        
        @media (max-width: 600px) {
            .container {
                padding: 20px;
            }
            
            h1 {
                font-size: 2em;
            }
            
            th, td {
                padding: 8px;
                font-size: 0.9em;
            }
            
            .date {
                display: none;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎮 TETRIS</h1>
        <p class="subtitle">Žebříček nejlepších hráčů</p>
        
        <?php if (count($highscores) > 0): ?>
            <table>
                <thead>
                    <tr>
                        <th>Pořadí</th>
                        <th>Jméno</th>
                        <th>Skóre</th>
                        <th>Datum</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($highscores as $index => $row): ?>
                        <tr>
                            <td>#<?php echo $index + 1; ?></td>
                            <td><?php echo htmlspecialchars($row['jmeno']); ?></td>
                            <td><?php echo number_format($row['skore'], 0, ',', ' '); ?></td>
                            <td class="date"><?php echo date('d.m.Y H:i', strtotime($row['datum'])); ?></td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
            <p class="last-updated">Poslední aktualizace: <?php echo date('d.m.Y H:i'); ?></p>
        <?php else: ?>
            <p class="no-scores">Zatím žádné skóre! 🎯<br>Buď první kdo zaznamená své skóre!</p>
        <?php endif; ?>
        
        <a href="<?php echo $_SERVER['PHP_SELF']; ?>" class="refresh-btn">🔄 Obnovit</a>
    </div>
</body>
</html>