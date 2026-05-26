<?php

declare(strict_types=1);

namespace EsaRobot\Tests\Functional;

use PHPUnit\Framework\TestCase;

final class RobotsCliTest extends TestCase
{
    private string $projectRoot;
    private string $pythonBinary;

    protected function setUp(): void
    {
        $this->projectRoot = dirname(__DIR__, 2);
        $this->pythonBinary = getenv('PYTHON_BINARY') ?: 'python';
    }

    /**
     * Verifies the challenge worked example through the CLI.
     * The test writes commands to a temporary file, runs the Python process, and
     * checks the final JSON lines on stdout.
     */
    public function testWorkedExampleWritesFinalRobotPositions(): void
    {
        $result = $this->runRobotsCli([
            ['type' => 'asteroid', 'size' => ['x' => 5, 'y' => 5]],
            ['type' => 'new-robot', 'position' => ['x' => 1, 'y' => 2], 'bearing' => 'north'],
            ['type' => 'move', 'movement' => 'turn-left'],
            ['type' => 'move', 'movement' => 'move-forward'],
            ['type' => 'move', 'movement' => 'turn-left'],
            ['type' => 'move', 'movement' => 'move-forward'],
            ['type' => 'move', 'movement' => 'turn-left'],
            ['type' => 'move', 'movement' => 'move-forward'],
            ['type' => 'move', 'movement' => 'turn-left'],
            ['type' => 'move', 'movement' => 'move-forward'],
            ['type' => 'move', 'movement' => 'move-forward'],
            ['type' => 'new-robot', 'position' => ['x' => 3, 'y' => 3], 'bearing' => 'east'],
            ['type' => 'move', 'movement' => 'move-forward'],
            ['type' => 'move', 'movement' => 'move-forward'],
            ['type' => 'move', 'movement' => 'turn-right'],
            ['type' => 'move', 'movement' => 'move-forward'],
            ['type' => 'move', 'movement' => 'move-forward'],
            ['type' => 'move', 'movement' => 'turn-right'],
            ['type' => 'move', 'movement' => 'move-forward'],
            ['type' => 'move', 'movement' => 'turn-right'],
            ['type' => 'move', 'movement' => 'turn-right'],
            ['type' => 'move', 'movement' => 'move-forward'],
        ]);

        self::assertSame(0, $result['exitCode']);
        self::assertSame('', $result['stderr']);
        self::assertSame([
            '{"type": "robot", "position": {"x": 1, "y": 3}, "bearing": "north"}',
            '{"type": "robot", "position": {"x": 5, "y": 1}, "bearing": "east"}',
        ], $this->stdoutLines($result));
    }

    /**
     * Verifies boundary wrap-around through the external CLI.
     * A north-facing robot at the top edge should wrap to y=0 after moving
     * forward.
     */
    public function testBoundaryWrapAroundThroughCli(): void
    {
        $result = $this->runRobotsCli([
            ['type' => 'asteroid', 'size' => ['x' => 5, 'y' => 5]],
            ['type' => 'new-robot', 'position' => ['x' => 5, 'y' => 5], 'bearing' => 'north'],
            ['type' => 'move', 'movement' => 'move-forward'],
        ]);

        self::assertSame(0, $result['exitCode']);
        self::assertSame('', $result['stderr']);
        self::assertSame([
            '{"type": "robot", "position": {"x": 5, "y": 0}, "bearing": "north"}',
        ], $this->stdoutLines($result));
    }

    /**
     * Verifies blank-line handling through file input.
     * The CLI should ignore empty lines while preserving and executing valid
     * JSON commands.
     */
    public function testBlankLinesAreIgnored(): void
    {
        $result = $this->runRobotsCliFromText(implode("\n", [
            '',
            '{"type": "asteroid", "size": {"x": 5, "y": 5}}',
            '',
            '{"type": "new-robot", "position": {"x": 1, "y": 2}, "bearing": "north"}',
            '',
        ]));

        self::assertSame(0, $result['exitCode']);
        self::assertSame('', $result['stderr']);
        self::assertSame([
            '{"type": "robot", "position": {"x": 1, "y": 2}, "bearing": "north"}',
        ], $this->stdoutLines($result));
    }

    /**
     * Verifies asteroid-only input through the CLI.
     * The process should succeed without writing stdout because no robot exists
     * to report.
     */
    public function testAsteroidOnlyInputSucceedsWithNoOutput(): void
    {
        $result = $this->runRobotsCli([
            ['type' => 'asteroid', 'size' => ['x' => 5, 'y' => 5]],
        ]);

        self::assertSame(0, $result['exitCode']);
        self::assertSame('', $result['stdout']);
        self::assertSame('', $result['stderr']);
    }

    /**
     * Verifies malformed JSON reporting through the CLI.
     * The process should fail, write no stdout, and identify the bad line on
     * stderr.
     */
    public function testInvalidJsonReturnsUsefulError(): void
    {
        $result = $this->runRobotsCliFromText(implode("\n", [
            '{"type": "asteroid", "size": {"x": 5, "y": 5}}',
            '{"type": "move"',
        ]));

        self::assertSame(1, $result['exitCode']);
        self::assertSame('', $result['stdout']);
        self::assertStringContainsString('error: Invalid JSON on line 2', $result['stderr']);
    }

    /**
     * Verifies empty instruction file handling.
     * The process should fail with the same first-command validation error used
     * by the Python parser.
     */
    public function testEmptyInstructionFileReturnsUsefulError(): void
    {
        $result = $this->runRobotsCliFromText('');

        self::assertSame(1, $result['exitCode']);
        self::assertSame('', $result['stdout']);
        self::assertStringContainsString('error: First command must be an asteroid message', $result['stderr']);
    }

    /**
     * Verifies first-command validation through the CLI.
     * A file that starts with a robot command should fail before any movement is
     * attempted.
     */
    public function testFirstCommandMustBeAsteroid(): void
    {
        $result = $this->runRobotsCli([
            ['type' => 'new-robot', 'position' => ['x' => 1, 'y' => 2], 'bearing' => 'north'],
        ]);

        self::assertSame(1, $result['exitCode']);
        self::assertSame('', $result['stdout']);
        self::assertStringContainsString('error: First command must be an asteroid message', $result['stderr']);
    }

    /**
     * Verifies out-of-bounds robot validation through the CLI.
     * The process should fail when a new robot is placed outside the inclusive
     * asteroid grid.
     */
    public function testNewRobotOutOfBoundsReturnsUsefulError(): void
    {
        $result = $this->runRobotsCli([
            ['type' => 'asteroid', 'size' => ['x' => 5, 'y' => 5]],
            ['type' => 'new-robot', 'position' => ['x' => 6, 'y' => 4], 'bearing' => 'north'],
        ]);

        self::assertSame(1, $result['exitCode']);
        self::assertSame('', $result['stdout']);
        self::assertStringContainsString('error: New robot cannot be initialised out of bounds', $result['stderr']);
    }

    /**
     * Verifies move-before-robot validation through the CLI.
     * The process should fail when the asteroid is defined but no robot has been
     * created before a move command arrives.
     */
    public function testMoveBeforeRobotReturnsUsefulError(): void
    {
        $result = $this->runRobotsCli([
            ['type' => 'asteroid', 'size' => ['x' => 5, 'y' => 5]],
            ['type' => 'move', 'movement' => 'turn-left'],
        ]);

        self::assertSame(1, $result['exitCode']);
        self::assertSame('', $result['stdout']);
        self::assertStringContainsString('error: No robot available to execute move command', $result['stderr']);
    }

    /**
     * Verifies unknown movement validation through the CLI.
     * The process should reject move commands whose movement value is outside
     * the allowed challenge movements.
     */
    public function testUnknownMovementReturnsUsefulError(): void
    {
        $result = $this->runRobotsCli([
            ['type' => 'asteroid', 'size' => ['x' => 5, 'y' => 5]],
            ['type' => 'new-robot', 'position' => ['x' => 1, 'y' => 2], 'bearing' => 'north'],
            ['type' => 'move', 'movement' => 'dance'],
        ]);

        self::assertSame(1, $result['exitCode']);
        self::assertSame('', $result['stdout']);
        self::assertStringContainsString('error: Unknown movement command: dance', $result['stderr']);
    }

    /**
     * Verifies unknown command validation through the CLI.
     * The process should reject messages whose type is not one of the allowed
     * command types.
     */
    public function testUnknownCommandTypeReturnsUsefulError(): void
    {
        $result = $this->runRobotsCli([
            ['type' => 'asteroid', 'size' => ['x' => 5, 'y' => 5]],
            ['type' => 'alien-anomaly', 'position' => ['x' => 0, 'y' => 1], 'bearing' => 'north'],
        ]);

        self::assertSame(1, $result['exitCode']);
        self::assertSame('', $result['stdout']);
        self::assertStringContainsString('error: Unknown command type: alien-anomaly', $result['stderr']);
    }

    /**
     * Verifies JSON shape validation through the CLI.
     * The process should reject a syntactically valid JSON value when it is not
     * an object command.
     */
    public function testNonObjectJsonCommandReturnsUsefulError(): void
    {
        $result = $this->runRobotsCliFromText(implode("\n", [
            '{"type": "asteroid", "size": {"x": 5, "y": 5}}',
            '"move-forward"',
        ]));

        self::assertSame(1, $result['exitCode']);
        self::assertSame('', $result['stdout']);
        self::assertStringContainsString('error: Command on line 2 must be a JSON object', $result['stderr']);
    }

    /**
     * Verifies missing file handling.
     * The CLI should fail cleanly and mention the missing path on stderr.
     */
    public function testMissingInstructionFileReturnsError(): void
    {
        $missingFile = $this->projectRoot . '/tests_php/fixtures/does-not-exist.txt';

        $result = $this->runProcess([$this->pythonBinary, 'robots.py', $missingFile]);

        self::assertSame(1, $result['exitCode']);
        self::assertSame('', $result['stdout']);
        self::assertStringContainsString('error:', $result['stderr']);
        self::assertStringContainsString('does-not-exist.txt', $result['stderr']);
    }

    /**
     * @param list<array<string, mixed>> $commands
     *
     * @return array{exitCode: int, stdout: string, stderr: string}
     */
    private function runRobotsCli(array $commands): array
    {
        $lines = array_map(
            static fn (array $command): string => json_encode($command, JSON_THROW_ON_ERROR),
            $commands,
        );

        return $this->runRobotsCliFromText(implode("\n", $lines));
    }

    /**
     * @return array{exitCode: int, stdout: string, stderr: string}
     */
    private function runRobotsCliFromText(string $instructions): array
    {
        $instructionsFile = tempnam(sys_get_temp_dir(), 'esa-robots-');
        self::assertIsString($instructionsFile);

        $bytesWritten = file_put_contents($instructionsFile, $instructions);
        self::assertIsInt($bytesWritten);

        try {
            return $this->runProcess([$this->pythonBinary, 'robots.py', $instructionsFile]);
        } finally {
            unlink($instructionsFile);
        }
    }

    /**
     * @param list<string> $command
     *
     * @return array{exitCode: int, stdout: string, stderr: string}
     */
    private function runProcess(array $command): array
    {
        $pipes = [];
        $process = proc_open(
            $command,
            [
                1 => ['pipe', 'w'],
                2 => ['pipe', 'w'],
            ],
            $pipes,
            $this->projectRoot,
        );

        self::assertIsResource($process);

        $stdout = stream_get_contents($pipes[1]);
        $stderr = stream_get_contents($pipes[2]);

        self::assertIsString($stdout);
        self::assertIsString($stderr);

        fclose($pipes[1]);
        fclose($pipes[2]);

        $exitCode = proc_close($process);

        return [
            'exitCode' => $exitCode,
            'stdout' => $stdout,
            'stderr' => $stderr,
        ];
    }

    /**
     * @param array{stdout: string} $result
     *
     * @return list<string>
     */
    private function stdoutLines(array $result): array
    {
        return explode("\n", trim($result['stdout']));
    }
}
